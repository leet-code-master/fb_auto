from fastapi import APIRouter, HTTPException
from api.modules.task.schema import (
    AccountTask, SubmitTasksRequest, SubmitTasksResponse,
    ConfigRequest, QueryProgressResponse, TaskResult, ProgressStatus
)
from api.modules.task.service import submit_account_tasks, get_pending_queue_tasks, clear_all_tasks, run_batch_tasks, \
    get_all_progress, get_progress_status

# 初始化APIRouter
router = APIRouter(prefix='/tasks', tags=['任务'])

@router.post("/submit", response_model=SubmitTasksResponse)
def submit_tasks(req: SubmitTasksRequest):
    """
    批量提交账号任务到队列
    """
    accounts = [acc.dict() for acc in req.accounts]
    task_ids = submit_account_tasks(accounts)
    return SubmitTasksResponse(task_ids=task_ids)

@router.get("/pending")
def get_queue_tasks():
    """
    查询当前等待队列中的任务
    """
    return get_pending_queue_tasks()

@router.delete("/clear")
def clear_tasks():
    """
    删除所有任务（包括队列、已完成、已失败、正在执行的任务，ID也重置）
    """
    clear_all_tasks()
    return {"success": True, "message": "All tasks (queue & history) have been cleared and ID reset."}

@router.post("/batch_run")
def batch_run_tasks(cfg: ConfigRequest):
    """
    根据配置批量执行队列任务
    """
    if cfg.thread_count < 1 or cfg.thread_count > 20:
        raise HTTPException(status_code=400, detail="thread_count must be between 1 and 20")
    run_batch_tasks(cfg.thread_count, cfg.is_back_mode)
    return {"success": True, "message": f"Batch execution started with {cfg.thread_count} threads, back_mode={cfg.is_back_mode}"}

@router.get("/results", response_model=QueryProgressResponse)
def get_all_results():
    """
    查询所有任务的执行结果
    """
    results = get_all_progress()
    return QueryProgressResponse(tasks=[
        TaskResult(**r) for r in results
    ])

@router.get("/progress", response_model=ProgressStatus)
def get_progress():
    """
    查询当前所有任务执行进度统计
    """
    return get_progress_status()