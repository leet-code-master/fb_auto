import threading
import time
from queue import Queue
from typing import List, Dict, Optional, Any
import itertools
import os

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ====== 路径和常量配置（请根据实际情况替换）======
# 获取当前文件的上三级目录作为项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# chromedriver 放在 static 目录下
CHROME_DRIVER_PATH = os.path.join(BASE_DIR, "static", "chromedriver")
# 目标登录页面、元素ID等（请根据实际页面调整）
LOGIN_URL = "https://example.com/login"
USERNAME_INPUT_ID = "username"
PASSWORD_INPUT_ID = "password"
LOGIN_BTN_ID = "login-btn"
SUCCESS_URL_KEYWORD = "dashboard"

# 任务状态常量
class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

# 单个任务对象，带锁，便于状态安全更新
class TaskItem:
    def __init__(self, task_id: int, username: str, password: str):
        self.task_id = task_id
        self.username = username
        self.password = password
        self.status = TaskStatus.PENDING
        self.result = None
        self.lock = threading.Lock()

# 全局任务相关对象和参数
task_id_counter = itertools.count(1)     # 自增任务ID生成器
tasks: Dict[int, TaskItem] = {}          # 全部任务（历史和当前）
task_queue = Queue()                     # 等待队列

# 配置参数（批量执行用）
current_thread_count = 2                 # 当前批量线程数
current_is_back_mode = True              # 当前是否后台模式

# 批量调度线程管理
batch_executor_lock = threading.Lock()   # 线程池操作锁
batch_executor_threads: List[threading.Thread] = []  # 线程对象列表
batch_executor_stop_event = threading.Event()        # 线程池停止标志

def selenium_login(username: str, password: str, is_back_mode=True) -> Dict:
    """
    用 Selenium 自动化登录，返回登录结果
    :param username: 账号
    :param password: 密码
    :param is_back_mode: 是否后台(headless)运行
    :return: dict，包括login字段（success/failed/error）
    """
    chrome_options = Options()
    if is_back_mode:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    try:
        driver.get(LOGIN_URL)
        driver.find_element(By.ID, USERNAME_INPUT_ID).send_keys(username)
        driver.find_element(By.ID, PASSWORD_INPUT_ID).send_keys(password)
        driver.find_element(By.ID, LOGIN_BTN_ID).click()
        time.sleep(2)  # 等待页面跳转
        if SUCCESS_URL_KEYWORD in driver.current_url:
            return {"login": "success", "username": username}
        else:
            return {"login": "failed", "username": username, "current_url": driver.current_url}
    except Exception as e:
        return {"login": "error", "username": username, "error": str(e)}
    finally:
        driver.quit()

def submit_account_tasks(accounts: List[dict]) -> List[int]:
    """
    批量提交账号任务到队列
    :param accounts: 包含账号密码的字典列表
    :return: 任务ID列表
    """
    task_ids = []
    for acc in accounts:
        task_id = next(task_id_counter)
        task = TaskItem(task_id, acc["username"], acc["password"])
        tasks[task_id] = task
        task_queue.put(task)
        task_ids.append(task_id)
    return task_ids

def get_pending_queue_tasks() -> list:
    """
    获取当前队列中未执行的任务（只读快照，非线程安全，仅展示用）
    :return: 等待队列任务的简要信息列表
    """
    pending = []
    with task_queue.mutex:
        for task in list(task_queue.queue):
            pending.append({
                "task_id": task.task_id,
                "username": task.username,
                "status": task.status,
            })
    return pending

def get_all_progress() -> List[dict]:
    """
    获取所有任务的执行状态和结果
    :return: 全部任务的详情列表
    """
    results = []
    for task_id, task in tasks.items():
        with task.lock:
            results.append({
                "task_id": task.task_id,
                "username": task.username,
                "status": task.status,
                "result": task.result
            })
    return results

def get_task_result(task_id: int) -> Optional[dict]:
    """
    查询单个任务的执行结果
    :param task_id: 任务ID
    :return: 该任务的详情（无则None）
    """
    task = tasks.get(task_id)
    if not task:
        return None
    with task.lock:
        return {
            "task_id": task.task_id,
            "username": task.username,
            "status": task.status,
            "result": task.result
        }

def clear_all_tasks():
    """
    清空所有任务（队列、历史、ID自增器）
    """
    global tasks, task_id_counter
    with task_queue.mutex:
        task_queue.queue.clear()
    tasks.clear()
    task_id_counter = itertools.count(1)

def get_progress_status() -> Dict:
    """
    获取执行进度的统计信息
    :return: 各状态任务数
    """
    total = len(tasks)
    done = running = pending = failed = 0
    for task in tasks.values():
        with task.lock:
            if task.status == TaskStatus.DONE:
                done += 1
            elif task.status == TaskStatus.RUNNING:
                running += 1
            elif task.status == TaskStatus.PENDING:
                pending += 1
            elif task.status == TaskStatus.FAILED:
                failed += 1
    return {
        "total": total,
        "done": done,
        "running": running,
        "pending": pending,
        "failed": failed
    }

def batch_worker(is_back_mode):
    """
    单个批量线程函数，从队列中取任务并执行
    :param is_back_mode: 是否后台模式
    """
    while not batch_executor_stop_event.is_set():
        try:
            # 等待获取一个任务
            task: TaskItem = task_queue.get(timeout=0.5)
        except Exception:
            continue
        with task.lock:
            task.status = TaskStatus.RUNNING
        # 执行selenium登录
        result = selenium_login(task.username, task.password, is_back_mode)
        with task.lock:
            if result.get("login") == "success":
                task.status = TaskStatus.DONE
            else:
                task.status = TaskStatus.FAILED
            task.result = result
        task_queue.task_done()

def run_batch_tasks(thread_count: int, is_back_mode: bool):
    """
    启动指定数量的线程并批量执行队列任务
    :param thread_count: 并发线程数
    :param is_back_mode: 是否后台模式
    """
    global batch_executor_threads, batch_executor_stop_event
    with batch_executor_lock:
        # 关闭已有线程池
        if batch_executor_threads:
            batch_executor_stop_event.set()
            for t in batch_executor_threads:
                t.join(timeout=2)
            batch_executor_threads = []
        batch_executor_stop_event = threading.Event()  # 新线程池停止标志
        # 启动新线程池
        for _ in range(thread_count):
            t = threading.Thread(target=batch_worker, args=(is_back_mode,), daemon=True)
            t.start()
            batch_executor_threads.append(t)

def stop_batch_tasks():
    """
    停止所有批量执行线程
    """
    global batch_executor_threads, batch_executor_stop_event
    with batch_executor_lock:
        if batch_executor_threads:
            batch_executor_stop_event.set()
            for t in batch_executor_threads:
                t.join(timeout=2)
            batch_executor_threads = []

# 程序退出时自动关闭线程池
import atexit
@atexit.register
def shutdown():
    stop_batch_tasks()