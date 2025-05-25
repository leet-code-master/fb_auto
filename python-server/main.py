from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from account_decode.router import router as account_router
from config_manage.router import router as config_router

app = FastAPI(title="FB自动化服务", description="提供账号解码和配置管理API")

# 配置CORS
origins = [
    "http://localhost",
    "http://localhost:5173",  # 默认Vite开发服务器端口
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(account_router, prefix="/api/account", tags=["账号解码"])
app.include_router(config_router, prefix="/api/config", tags=["配置管理"])

@app.get("/")
async def root():
    return {"message": "欢迎使用FB自动化服务API"}    