from pydantic import BaseModel, Field
from typing import List, Any, Optional


class BaseResp(BaseModel):
    code: int = Field(description="状态码")
    message: str = Field(description="信息")
    data: List = Field(description="数据")

class ResAntTable(BaseModel):
    success: bool = Field(description="状态码")
    data: List = Field(description="数据")
    message: str = Field(description="信息")
    total: int = Field(description="总条数")
