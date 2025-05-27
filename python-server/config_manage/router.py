from fastapi import APIRouter, HTTPException
from .schema import ConfigUpdateRequest, ConfigResponse
from .service import ConfigService

router = APIRouter()
service = ConfigService()

@router.get("/all", response_model=ConfigResponse)
async def get_all_config():
    """获取所有配置"""
    return service.get_all_config()

@router.post("/update", response_model=ConfigResponse)
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    return service.update_config(request)

@router.get("/{key}", response_model=ConfigResponse)
async def get_config(key: str):
    """获取单个配置项"""
    return service.get_config(key)    