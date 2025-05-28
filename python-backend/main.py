from fastapi import FastAPI
from core import Router

from config import settings

application = FastAPI(
    debug=settings.APP_DEBUG,
    docs_url=None,
    redoc_url=None,
)

# 路由
application.include_router(Router.router)
app = application
