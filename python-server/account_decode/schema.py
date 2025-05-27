from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime


class AccountItem(BaseModel):
    account: str
    password: str
    twoFA: str
    email: str
    emailPassword: str
    spareEmail: str = ""
   

class AccountDecodeStartRequest(BaseModel):
    accounts: List[AccountItem] = []
    threadCount: int = 10
    isBackMode: bool = True
    executionModules: List[int] = []


class AccountDecodeStartResponse(BaseModel):
    success: bool
    data: Any = None
    message: str = ""