from typing import List
from fastapi import APIRouter, BackgroundTasks, HTTPException
from .service import task_service
from .schema import (
    AccountResult,
    TaskRequest,
    BatchTaskResponse,
    AccountDetailResponse,
    AccountInfo,
    ExecutionModule
)
from .utils import format_datetime

router = APIRouter(prefix="/v3")


@router.post("/execute", response_model=BatchTaskResponse)
async def execute_accounts(request: TaskRequest, background_tasks: BackgroundTasks):
    batch_id, task_ids = task_service.create_batch(request)
    background_tasks.add_task(
        task_service.execute_batch_in_background,
        request,
        batch_id
    )
    return {"batch_id": batch_id, "task_ids": task_ids}


@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: int):
    status = task_service.get_batch_status(batch_id)
    progress = task_service.get_batch_progress(batch_id)
    progress_percent = 0
    total = progress.get("total", 0)
    completed = progress.get("success", 0) + progress.get("failed", 0) + progress.get("cancelled", 0)
    if total > 0:
        progress_percent = round((completed / total) * 100, 2)
    create_time = task_service.get_batch_create_time(batch_id)
    return {
        "batch_id": batch_id,
        "status": status,
        "create_time": format_datetime(create_time),
        "progress": {
            "total_tasks": total,
            "pending": progress.get("pending", 0),
            "running": progress.get("running", 0),
            "success": progress.get("success", 0),
            "failed": progress.get("failed", 0),
            "cancelled": progress.get("cancelled", 0),
            "completed": completed,
            "progress_percent": progress_percent
        }
    }


@router.get("/results/{batch_id}", response_model=List[AccountResult])
async def get_batch_results(batch_id: int):
    results = task_service.get_batch_results(batch_id)
    # 格式化每个任务的时间
    for r in results:
        if hasattr(r, "create_time") and r.create_time:
            r.create_time = format_datetime(r.create_time)
        if hasattr(r, "complete_time") and r.complete_time:
            r.complete_time = format_datetime(r.complete_time)
    return results
    # return task_service.get_batch_results(batch_id)


@router.get("/task/{task_id}", response_model=AccountDetailResponse)
async def get_task_detail(task_id: int):
    task_orm = task_service.get_task_orm(task_id)
    if not task_orm:
        raise HTTPException(status_code=404, detail="Task not found")
    account_info = AccountInfo.parse_obj(task_orm.account_info)
    execution_modules = [ExecutionModule(mod) for mod in (task_orm.execution_modules or [])]
    return AccountDetailResponse(
        task_id=task_orm.id,
        username=task_orm.username,
        status=task_orm.status,
        result=task_orm.result,
        error=task_orm.error,
        create_time=format_datetime(task_orm.create_time),
        complete_time=format_datetime(task_orm.complete_time),
        account_info=account_info,
        execution_modules=execution_modules,
        thread_id=task_orm.thread_id,
        browser_type=task_orm.browser_type or "Unknown"
    )


@router.put("/cancel/{batch_id}")
async def cancel_batch(batch_id: int):
    success = task_service.cancel_batch(batch_id)
    if not success:
        raise HTTPException(status_code=400, detail="Batch cannot be cancelled or batch id not found")
    return {"message": "Batch cancelled successfully"}


@router.get("/batch")
async def get_all_batch_detail():
    """
    查询所有批次任务详情（含批次id、状态、创建时间等）
    """
    batches = task_service.get_all_batches()
    return [
        {
            "batch_id": b.id,
            "status": b.status,
            "create_time": format_datetime(b.create_time),
            "task_count": b.task_count
        }
        for b in batches
    ]
