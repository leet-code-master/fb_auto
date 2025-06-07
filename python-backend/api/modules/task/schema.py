from pydantic import BaseModel
from typing import List, Optional, Any

# 单个账号任务模型
class AccountTask(BaseModel):
    username: str
    password: str
    two_fa: str
    email: str
    email_password: str
    spare_email: str

# 批量提交账号任务请求
class SubmitTasksRequest(BaseModel):
    accounts: List[AccountTask]

# 批量提交账号任务响应
class SubmitTasksResponse(BaseModel):
    task_ids: List[int]

# 配置批量执行参数的请求
class ConfigRequest(BaseModel):
    thread_count: int         # 并发线程数
    is_back_mode: bool        # 是否后台模式（headless）

# 设置并发线程数请求
class SetConcurrencyRequest(BaseModel):
    concurrency: int

# 设置并发线程数响应
class SetConcurrencyResponse(BaseModel):
    success: bool
    current_concurrency: int

# 单个任务的执行结果模型
class TaskResult(BaseModel):
    task_id: int
    username: str
    status: str          # pending, running, done, failed
    result: Optional[Any]

# 所有任务的执行结果列表响应
class QueryProgressResponse(BaseModel):
    tasks: List[TaskResult]

# 执行进度状态模型
class ProgressStatus(BaseModel):
    total: int   # 总任务数
    done: int    # 完成数
    running: int # 正在执行数
    pending: int # 等待队列数
    failed: int  # 失败数