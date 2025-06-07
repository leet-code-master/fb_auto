import itertools
from typing import List, Dict

from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.index import get_chrome_driver

# 使用 itertools 来生成自增ID
id_generator = itertools.count(1)

def parse_account(account):
    try:
        driver = get_chrome_driver(False)
        driver.get(
            'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=9199bf20-a13f-4107-85dc-02114787ef48&scope=https%3A%2F%2Foutlook.office.com%2F.default%20openid%20profile%20offline_access&redirect_uri=https%3A%2F%2Foutlook.live.com%2Fmail%2F&client-request-id=9ba2251e-3aa7-0d43-75ad-3cb67dfb68d8&response_mode=fragment&client_info=1&prompt=select_account&nonce=0197208e-08d2-7d5a-9e1c-52f8a1773021&state=eyJpZCI6IjAxOTcyMDhlLTA4ZDItNzEzMS05YTNlLWYwNTJiYzMyYzc2NSIsIm1ldGEiOnsiaW50ZXJhY3Rpb25UeXBlIjoicmVkaXJlY3QifX0%3D&claims=%7B%22access_token%22%3A%7B%22xms_cc%22%3A%7B%22values%22%3A%5B%22CP1%22%5D%7D%7D%7D&x-client-SKU=msal.js.browser&x-client-VER=4.12.0&response_type=code&code_challenge=LmKW-Q6Vd7iDGfqfARJhrAPUj04FpcGwa0fnc7fJP-U&code_challenge_method=S256&cobrandid=ab0455a0-8d03-46b9-b18b-df2f57b9e44c&fl=dob,flname,wld')
        driver.implicitly_wait(5)
        account_dom = driver.find_element(By.XPATH, '//*[@id="i0116"]')
        account_dom.send_keys(account.account)

        next_dom = driver.find_element(By.ID, "idSIButton9")
        next_dom.click()
        status = "Success"
        try:
            username_err_dom = driver.find_element(By.XPATH, '//*[@id="usernameError"]')
            status = "账号不存在"
            driver.quit()
        except NoSuchElementException:
            pass


        account_id = next(id_generator)  # 生成自增ID
        return {'id': account_id, 'account_info': account, 'status': status}
    except Exception as e:
        return None, str(e)  # 返回异常信息


def login_baidu(account):
    driver = get_chrome_driver(False)
    driver.get('https://www.baidu.com/')
    driver.implicitly_wait(2)
    status = ''
    try:
        login_btn_dom = driver.find_element(By.ID, 's-top-loginbtn')
        login_btn_dom.click()

        username_input_dom = driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_11__userName"]')
        username_input_dom.send_keys(account.account)

        password_input_dom = driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_11__password"]')
        password_input_dom.send_keys(account.password)

        driver.find_element(By.ID, 'TANGRAM__PSP_11__isAgree').click()
        driver.find_element(By.ID, 'TANGRAM__PSP_11__submit').click()

        # 使用显式等待等待错误提示元素出现
        is_error = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'TANGRAM__PSP_11__error'))
        )
        if is_error:
            error_dom = driver.find_element(By.ID, 'TANGRAM__PSP_11__error')
            status = '账号或密码错误' if error_dom else '未获取到Error节点'

        # error_dom = driver.find_element(By.ID, 'TANGRAM__PSP_11__error')
        # status = error_dom.get_attribute('innerText') if error_dom else '未获取到Error节点'
    except NoSuchElementException:
        pass

    account_id = next(id_generator)  # 生成自增ID
    return {'id': account_id, 'account_info': account, "status": status}
    # driver.quit()

from queue import Queue
import threading
# ====== 任务状态和结构 ======
class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
class TaskItem:
    def __init__(self, task_id: int, account: str, password: str):
        self.task_id = task_id
        self.account = account
        self.password = password
        self.status = TaskStatus.PENDING
        self.result = None
        self.lock = threading.Lock()
task_id_counter = itertools.count(1)
tasks: Dict[int, TaskItem] = {}
task_queue = Queue()
def submit_account_tasks(accounts: List[dict]) -> List[int]:
    """
    提交任务到队列中
    """
    task_ids = []
    for acc in accounts:
        task_id = next(task_id_counter)
        task = TaskItem(task_id, acc["account"], acc["password"])
        tasks[task_id] = task
        task_queue.put(task)
        task_ids.append(task_id)
    return task_ids


def get_pending_queue_tasks() -> list:
    """
    查询当前队列中的任务列表
    """
    pending = []
    with task_queue.mutex:
        for task in list(task_queue.queue):
            pending.append({
                "id": task.task_id,
                "account": task.account,
                "status": task.status,
            })
    return pending

def clear_pending_queue_tasks():
    """清空队列中所有尚未开始的任务（不影响已在执行/已完成的任务）"""
    with task_queue.mutex:
        task_queue.queue.clear()


def clear_all_tasks():
    """
    清空所有任务，包括队列中的、已完成的、已失败的、正在执行的任务，并重置自增ID
    """
    global tasks, task_id_counter
    with task_queue.mutex:
        task_queue.queue.clear()
    tasks.clear()
    # ID从1重新计数
    task_id_counter = itertools.count(1)
