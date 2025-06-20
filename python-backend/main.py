import os
from fastapi import FastAPI
from core import Router, Events
from fastapi.middleware.cors import CORSMiddleware
from config import settings

from api.modules.worker.service import engine, executor
from api.modules.worker.utils import clear_all_tables
import psutil

application = FastAPI(
    debug=settings.APP_DEBUG,
    docs_url=None,
    redoc_url=None,
)

# 只在开发环境自动清空所有表
if os.environ.get("ENV") == "dev":
    clear_all_tables(engine)

# 事件监听
application.add_event_handler("startup", Events.startup(application))
application.add_event_handler("shutdown", Events.stopping(application))

# 配置CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # 默认Vite开发服务器端口
]
application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 路由
application.include_router(Router.router)
app = application
@app.get("/")
async def root():
    return {"message": "欢迎使用FB自动化服务API"}

@app.on_event("shutdown")
def shutdown_event():
    executor.shutdown(wait=False, cancel_futures=True)
    current = psutil.Process(os.getpid())
    for child in current.children(recursive=True):
        name = child.name().lower()
        if 'chrome' in name or 'chromedriver' in name:
            try:
                child.kill()
            except Exception:
                pass