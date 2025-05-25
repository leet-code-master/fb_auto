from .schema import AccountDecodeRequest, AccountDecodeItem, AccountDecodeResponse
import random
import string
from datetime import datetime

class AccountDecodeService:
    def __init__(self):
        self.tasks = []
        self.next_task_id = 1
        
    def decode_account(self, request: AccountDecodeRequest) -> AccountDecodeResponse:
        try:
            # 模拟解码逻辑
            decoded_items = self._process_account_string(request.account_str)
            return AccountDecodeResponse(
                success=True,
                data=decoded_items,
                message="解码成功"
            )
        except Exception as e:
            return AccountDecodeResponse(
                success=False,
                message=f"解码失败: {str(e)}"
            )
            
    def add_to_queue(self, request: AccountDecodeRequest) -> AccountDecodeResponse:
        try:
            # 创建新任务
            task_id = self.next_task_id
            self.next_task_id += 1
            
            # 模拟分割账号字符串
            accounts = request.account_str.split("|")
            
            for account in accounts:
                if account.strip():
                    task = AccountDecodeItem(
                        id=task_id,
                        account=account.strip()
                    )
                    self.tasks.append(task)
            
            return AccountDecodeResponse(
                success=True,
                message=f"已添加 {len(accounts)} 个账号到处理队列"
            )
        except Exception as e:
            return AccountDecodeResponse(
                success=False,
                message=f"添加到队列失败: {str(e)}"
            )
            
    def get_task_list(self) -> List[AccountDecodeItem]:
        return self.tasks
    
    def _process_account_string(self, account_str: str) -> List[AccountDecodeItem]:
        # 模拟处理账号字符串
        items = []
        accounts = account_str.split("|")
        
        for account in accounts:
            if account.strip():
                task_id = self.next_task_id
                self.next_task_id += 1
                
                # 随机生成状态
                status = random.choice(["成功", "失败", "进行中"])
                
                # 随机生成日志
                log_result = "".join(random.choices(string.ascii_letters + string.digits, k=20)) if status != "进行中" else None
                
                items.append(AccountDecodeItem(
                    id=task_id,
                    account=account.strip(),
                    status=status,
                    log_result=log_result
                ))
                
        return items    