from fastapi import APIRouter, BackgroundTasks
from api.modules.account.schema import DecodeRequest, DecodeAccounts
from core.Response import success
from concurrent.futures import ThreadPoolExecutor, as_completed


from api.modules.account.service import login_baidu, submit_account_tasks, get_pending_queue_tasks

router = APIRouter(prefix='/account', tags=['账号解码'])

executor = ThreadPoolExecutor()
@router.post('/start')
async def start(request: DecodeRequest):
    params = DecodeRequest( accounts = request.accounts, thread_count = request.thread_count,is_back_mode = request.is_back_mode,execution_modules = request.execution_modules)
    data = await start_chrome(params)

    return success(msg=f"传入{len(request.accounts)}条数据", data=data)

async def start_chrome(params:DecodeRequest):
    try:
        result = []
        with  ThreadPoolExecutor(max_workers=params.thread_count) as executor:
            # 提交任务到线程池
            tasks = {executor.submit(login_baidu, account): account for account in params.accounts}

            for future in  as_completed(tasks):
                account = tasks[future]
                try:
                    # result.append(future)
                    # 获取异步任务的结果并添加到结果列表
                    task_result = future.result()
                    result.append(task_result)
                except Exception as e:
                    print(f"An error occurred for account {account}: {str(e)}")
        return result
    except Exception as e:
        return f"Failed to parse account {params}: {str(e)}"


@router.post('/task')
async def start_task(params: DecodeRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(start_chrome, params)
    return {'message': '任务开始执行'}

@router.post("/stop_tasks")
async def stop_tasks():
    global executor
    executor.shutdown(wait=False)
    executor = ThreadPoolExecutor()
    return {"message": "队列的任务都已停止"}


@router.post('/add_queue')
async def add_queue(req: DecodeAccounts):
    accounts = [acc.dict() for acc in req.accounts]
    task_ids = submit_account_tasks(accounts)
    print(f"task_ids: {task_ids}")
    return success(msg=f"添加{len(task_ids)}条数据到队列")

@router.get("/pending")
def get_pending_queues():
    """
    查询当前等待队列中的任务内容
    """
    return get_pending_queue_tasks()

