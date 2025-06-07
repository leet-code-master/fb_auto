from fastapi import FastAPI
from core import Router, Events
from fastapi.middleware.cors import CORSMiddleware
from config import settings

application = FastAPI(
    debug=settings.APP_DEBUG,
    docs_url=None,
    redoc_url=None,
)

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