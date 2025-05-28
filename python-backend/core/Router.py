from api.index import api_router
from fastapi import APIRouter


router = APIRouter()
# API路由
router.include_router(api_router)

