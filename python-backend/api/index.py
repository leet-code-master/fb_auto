from fastapi import APIRouter
from api.modules import account_decode

api_router = APIRouter(prefix="/api")
api_router.include_router(account_decode.router, tags=["账号解码"])