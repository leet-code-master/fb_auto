from fastapi import APIRouter
from api.modules.account import router as module_router
from api.modules.task import router as task_router

api_router = APIRouter(prefix="/api")
api_router.include_router(module_router.router, tags=["账号解码"])
api_router.include_router(task_router.router, tags=["提交任务"])