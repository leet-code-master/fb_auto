from fastapi import APIRouter, HTTPException
from .schema import AccountDecodeRequest, AccountDecodeResponse
from .service import AccountDecodeService

router = APIRouter()
service = AccountDecodeService()

@router.post("/decode", response_model=AccountDecodeResponse)
async def decode_account(request: AccountDecodeRequest):
    """解码账号字符串"""
    return service.decode_account(request)

@router.post("/queue", response_model=AccountDecodeResponse)
async def add_to_queue(request: AccountDecodeRequest):
    """添加账号到处理队列"""
    return service.add_to_queue(request)

@router.get("/tasks", response_model=list[AccountDecodeResponse])
async def get_tasks():
    """获取所有任务"""
    return service.get_task_list()    