from fastapi import APIRouter, HTTPException
from .schema import (
    AccountDecodeStartResponse,
    AccountDecodeStartRequest,
)
# from .service import AccountDecodeService

router = APIRouter()
# service = AccountDecodeService()


@router.post("/start")
async def decode_account(request: AccountDecodeStartRequest):
    # """解码账号字符串"""

    return AccountDecodeStartResponse(success=True, message="success", data=request)