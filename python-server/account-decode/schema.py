from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AccountDecodeRequest(BaseModel):
    account_str: str = Field(..., description="账号字符串")
    
class AccountDecodeItem(BaseModel):
    id: int
    account: str
    status: str = "待处理"
    log_result: Optional[str] = None
    update_time: datetime = Field(default_factory=datetime.now)
    
class AccountDecodeResponse(BaseModel):
    success: bool
    data: Optional[List[AccountDecodeItem]] = None
    message: str = ""    