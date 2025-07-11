import threading
from datetime import datetime
from core.DataBase import db_session
from .models import BatchTaskORM, AccountTaskORM
from .schema import TaskStatus, AccountResult, TaskRequest
from typing import List, Dict, Any, Optional
from .browser_worker import login_facebook
from concurrent.futures import ProcessPoolExecutor
import logging
from queue import Queue
from sqlalchemy import func

# 全局唯一进程池
executor = ProcessPoolExecutor(max_workers=20)
logger = logging.getLogger("worker_service")

class BatchDetail:
    def __init__(self, id, status, create_time, task_count):
        self.id = id
        self.status = status
        self.create_time = create_time
        self.task_count = task_count

class DBTaskService:
    def __init__(self):
        self.lock = threading.RLock()
        self.cancelled_batches = set()

    def create_batch(self, request: TaskRequest) -> (int, List[int]):
        with db_session() as db:
            batch = BatchTaskORM(status=TaskStatus.PENDING)
            db.add(batch)
            db.commit()
            db.refresh(batch)
            batch_id = batch.id
            task_ids = []
            for acc in request.accounts:
                task = AccountTaskORM(
                    batch_id=batch_id,
                    username=acc.username,
                    status=TaskStatus.PENDING,
                    create_time=datetime.now(),
                    account_info=acc.dict(),
                    execution_modules=[mod.value for mod in request.execution_modules]
                )
                db.add(task)
                db.flush()
                task_ids.append(task.id)
            db.commit()
            return batch_id, task_ids

    def cancel_batch(self, batch_id: int) -> bool:
        with db_session() as db:
            batch = db.query(BatchTaskORM).filter_by(id=batch_id).first()
            if not batch or batch.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                return False
            batch.status = TaskStatus.CANCELLED
            db.query(AccountTaskORM).filter_by(batch_id=batch_id)\
                .filter(AccountTaskORM.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))\
                .update({AccountTaskORM.status: TaskStatus.CANCELLED, AccountTaskORM.complete_time: datetime.now()},
                        synchronize_session=False)
            db.commit()
            self.cancelled_batches.add(batch_id)
            return True

    def is_batch_cancelled(self, batch_id: int) -> bool:
        return batch_id in self.cancelled_batches

    def execute_batch_in_background(self, request: TaskRequest, batch_id: int):
        with db_session() as db:
            tasks = db.query(AccountTaskORM).filter_by(batch_id=batch_id).all()
        task_queue = Queue()
        for task in tasks:
            if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
                task_queue.put(task.id)
        running = []
        while not task_queue.empty() or running:
            while len(running) < request.thread_count and not task_queue.empty():
                tid = task_queue.get()
                with db_session() as db:
                    t = db.query(AccountTaskORM).filter_by(id=tid).first()
                fut = executor.submit(login_facebook, t.account_info, t.execution_modules, request.is_back_mode)
                running.append((tid, fut))
                self.update_task_status(tid, TaskStatus.RUNNING)
            # 检查完成
            for tid, fut in running[:]:
                if fut.done():
                    try:
                        res = fut.result(timeout=120)
                        if res.get("success"):
                            self.update_task_status(tid, TaskStatus.SUCCESS, result=res)
                        else:
                            self.update_task_status(tid, TaskStatus.FAILED, result=res, error=res.get("error"))
                    except Exception as e:
                        logger.exception(f"Task {tid} failed: {e}")
                        self.update_task_status(tid, TaskStatus.FAILED, error=str(e))
                    running.remove((tid, fut))
            # 检查是否被取消
            if self.is_batch_cancelled(batch_id):
                for tid, fut in running:
                    self.update_task_status(tid, TaskStatus.CANCELLED)
                break

    def update_task_status(self, task_id: int, status: TaskStatus, result: Any = None, error: str = None):
        with db_session() as db:
            task = db.query(AccountTaskORM).filter_by(id=task_id).first()
            if task:
                task.status = status
                task.complete_time = datetime.now()
                if result is not None:
                    task.result = result
                if error is not None:
                    task.error = error
                db.commit()
                self.update_batch_status_if_needed(task.batch_id, db)

    def update_batch_status_if_needed(self, batch_id: int, db=None):
        close_db = False
        if db is None:
            db = next(db_session())
            close_db = True
        try:
            batch = db.query(BatchTaskORM).filter_by(id=batch_id).first()
            if not batch:
                return
            tasks = db.query(AccountTaskORM).filter_by(batch_id=batch_id).all()
            if not tasks:
                return
            all_status = [t.status for t in tasks]
            if all(s in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED] for s in all_status):
                if all(s == TaskStatus.SUCCESS for s in all_status):
                    batch.status = TaskStatus.SUCCESS
                elif all(s == TaskStatus.CANCELLED for s in all_status):
                    batch.status = TaskStatus.CANCELLED
                elif any(s == TaskStatus.SUCCESS for s in all_status):
                    batch.status = TaskStatus.COMPLETED
                else:
                    batch.status = TaskStatus.FAILED
                db.commit()
        finally:
            if close_db:
                db.close()

    def get_batch_status(self, batch_id: int) -> TaskStatus:
        with db_session() as db:
            batch = db.query(BatchTaskORM).filter_by(id=batch_id).first()
            return batch.status if batch else TaskStatus.FAILED

    def get_batch_progress(self, batch_id: int) -> dict:
        with db_session() as db:
            tasks = db.query(AccountTaskORM).filter_by(batch_id=batch_id).all()
            stat = dict(total=len(tasks), pending=0, running=0, success=0, failed=0, cancelled=0)
            for t in tasks:
                s = t.status
                if s == TaskStatus.PENDING:
                    stat['pending'] += 1
                elif s == TaskStatus.RUNNING:
                    stat['running'] += 1
                elif s == TaskStatus.SUCCESS:
                    stat['success'] += 1
                elif s == TaskStatus.FAILED:
                    stat['failed'] += 1
                elif s == TaskStatus.CANCELLED:
                    stat['cancelled'] += 1
            return stat

    def get_batch_results(self, batch_id: int) -> List[AccountResult]:
        with db_session() as db:
            tasks = db.query(AccountTaskORM).filter_by(batch_id=batch_id).all()
            return [
                AccountResult(
                    task_id=t.id,
                    username=t.username,
                    status=t.status,
                    result=t.result,
                    error=t.error,
                    create_time=t.create_time,
                    complete_time=t.complete_time
                ) for t in tasks
            ]

    def get_task_orm(self, task_id: int):
        with db_session() as db:
            return db.query(AccountTaskORM).filter_by(id=task_id).first()

    def get_task_detail(self, task_id: int) -> Optional[AccountResult]:
        with db_session() as db:
            t = db.query(AccountTaskORM).filter_by(id=task_id).first()
            if not t:
                return None
            return AccountResult(
                task_id=t.id,
                username=t.username,
                status=t.status,
                result=t.result,
                error=t.error,
                create_time=t.create_time,
                complete_time=t.complete_time
            )

    def get_batch_create_time(self, batch_id: int):
        with db_session() as db:
            batch = db.query(BatchTaskORM).filter_by(id=batch_id).first()
            return batch.create_time if batch else None

    def get_all_batches(self) -> List[BatchDetail]:
        with db_session() as db:
            batches = db.query(BatchTaskORM).all()
            batch_ids = [b.id for b in batches]
            if not batch_ids:
                return []
            counts = db.query(AccountTaskORM.batch_id, func.count(AccountTaskORM.id)).filter(
                AccountTaskORM.batch_id.in_(batch_ids)
            ).group_by(AccountTaskORM.batch_id).all()
            count_map = {bid: cnt for bid, cnt in counts}
            return [
                BatchDetail(
                    id=b.id,
                    status=b.status,
                    create_time=b.create_time,
                    task_count=count_map.get(b.id, 0)
                ) for b in batches
            ]

task_service = DBTaskService()