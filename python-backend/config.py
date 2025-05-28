

from pydantic_settings import BaseSettings
from typing import List


class Config(BaseSettings):
    # 调试模式
    APP_DEBUG: bool = True
    # 跨域请求
    CORS_ORIGINS: List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List = ["*"]
    CORS_ALLOW_HEADERS: List = ["*"]


settings = Config()
