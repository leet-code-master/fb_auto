from pydantic import BaseModel
from typing import List

class Account(BaseModel):
    account: str
    password: str
    two_fa: str
    email: str
    email_password: str
    spare_email: str = ''

class DecodeRequest(BaseModel):
    accounts: List[Account] = []
    thread_count: int
    is_back_mode: bool = False
    execution_modules: List[int] = []

class DecodeAccounts(BaseModel):
    accounts: List[Account] = []