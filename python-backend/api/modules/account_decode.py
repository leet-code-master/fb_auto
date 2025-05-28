
from fastapi import Request, Query, APIRouter


router = APIRouter(prefix='/account', tags=['账号解码'])

@router.post('/start')
async def start(request: Request):
    return {'message': request}