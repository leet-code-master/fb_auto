from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ExecutionModule(int, Enum):
    MODULE_1 = 1
    MODULE_2 = 2


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AccountInfo(BaseModel):
    username: str
    password: str
    two_fa: Optional[str] = None
    email: Optional[str] = None
    email_password: Optional[str] = None
    spare_email: Optional[str] = None


class TaskRequest(BaseModel):
    accounts: List[AccountInfo]
    thread_count: int = Field(10, gt=0, le=20, description="并发线程数")
    is_back_mode: bool = Field(False, description="无头模式")
    execution_modules: List[ExecutionModule]


class AccountResult(BaseModel):
    task_id: int
    username: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    create_time: datetime
    complete_time: Optional[datetime] = None


class BatchTaskResponse(BaseModel):
    batch_id: int
    task_ids: List[int]


class AccountDetailResponse(AccountResult):
    account_info: AccountInfo
    execution_modules: List[ExecutionModule]
    thread_id: Optional[int] = None
    browser_type: str

    class Config:
        extra = "allow"
