import threading
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future
from queue import Queue
import itertools

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ================== 配置 ==================
CHROME_DRIVER_PATH = None  # 如果chromedriver非PATH目录，请填写路径
LOGIN_URL = "https://example.com/login"  # TODO: 修改为你的登录页面
USERNAME_INPUT_ID = "username"           # TODO: 修改为实际输入框ID
PASSWORD_INPUT_ID = "password"           # TODO: 修改为实际输入框ID
LOGIN_BTN_ID = "login-btn"               # TODO: 修改为实际按钮ID
SUCCESS_URL_KEYWORD = "dashboard"        # TODO: 登录成功后url关键字或其它判据

app = FastAPI()

# ================== 数据结构 ==================
class AccountTask(BaseModel):
    username: str
    password: str

class SubmitTasksRequest(BaseModel):
    accounts: List[AccountTask]

class SubmitTasksResponse(BaseModel):
    task_ids: List[int]

class SetConcurrencyRequest(BaseModel):
    concurrency: int

class SetConcurrencyResponse(BaseModel):
    success: bool
    current_concurrency: int

class TaskResult(BaseModel):
    task_id: int
    username: str
    status: str          # pending, running, done, failed
    result: Optional[Any]

class QueryProgressResponse(BaseModel):
    tasks: List[TaskResult]

# ================== 任务管理 ==================
class TaskStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

class TaskItem:
    def __init__(self, task_id: int, username: str, password: str):
        self.task_id = task_id
        self.username = username
        self.password = password
        self.status = TaskStatus.PENDING
        self.result = None
        self.lock = threading.Lock()

# 全局自增ID
task_id_counter = itertools.count(1)
# 全局任务缓存
tasks: Dict[int, TaskItem] = {}
# 任务队列
task_queue = Queue()
# 默认并发
current_concurrency = 2
executor = ThreadPoolExecutor(max_workers=current_concurrency)
# 控制worker线程退出
stop_event = threading.Event()

# ================== 核心任务函数 ==================
def selenium_login(username: str, password: str) -> Dict:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=chrome_options)
    driver.set_page_load_timeout(30)
    try:
        driver.get(LOGIN_URL)
        driver.find_element(By.ID, USERNAME_INPUT_ID).send_keys(username)
        driver.find_element(By.ID, PASSWORD_INPUT_ID).send_keys(password)
        driver.find_element(By.ID, LOGIN_BTN_ID).click()
        time.sleep(2)
        if SUCCESS_URL_KEYWORD in driver.current_url:
            return {"login": "success", "username": username}
        else:
            return {"login": "failed", "username": username, "current_url": driver.current_url}
    except Exception as e:
        return {"login": "error", "username": username, "error": str(e)}
    finally:
        driver.quit()

def worker_loop():
    while not stop_event.is_set():
        try:
            task: TaskItem = task_queue.get(timeout=0.5)
        except Exception:
            continue
        with task.lock:
            task.status = TaskStatus.RUNNING
        result = selenium_login(task.username, task.password)
        with task.lock:
            task.status = TaskStatus.DONE if result.get("login") == "success" else TaskStatus.FAILED
            task.result = result
        task_queue.task_done()

# worker线程管理
worker_threads: List[threading.Thread] = []

def start_workers(n: int):
    global worker_threads
    stop_event.clear()
    worker_threads = []
    for _ in range(n):
        t = threading.Thread(target=worker_loop, daemon=True)
        t.start()
        worker_threads.append(t)

def stop_workers():
    stop_event.set()
    for t in worker_threads:
        t.join(timeout=2)
    worker_threads.clear()

def reset_workers(n: int):
    stop_workers()
    start_workers(n)

# 启动初始worker
start_workers(current_concurrency)

# ================== FastAPI接口 ==================

@app.post("/api/tasks/submit", response_model=SubmitTasksResponse)
def submit_tasks(req: SubmitTasksRequest):
    task_ids = []
    for acc in req.accounts:
        task_id = next(task_id_counter)
        task = TaskItem(task_id, acc.username, acc.password)
        tasks[task_id] = task
        task_queue.put(task)
        task_ids.append(task_id)
    return SubmitTasksResponse(task_ids=task_ids)

@app.post("/api/tasks/concurrency", response_model=SetConcurrencyResponse)
def set_concurrency(req: SetConcurrencyRequest):
    global current_concurrency
    if req.concurrency < 1 or req.concurrency > 20:
        raise HTTPException(status_code=400, detail="concurrency must be between 1 and 20")
    current_concurrency = req.concurrency
    reset_workers(current_concurrency)
    return SetConcurrencyResponse(success=True, current_concurrency=current_concurrency)

@app.get("/api/tasks/progress", response_model=QueryProgressResponse)
def query_progress():
    results = []
    for task_id, task in tasks.items():
        with task.lock:
            results.append(TaskResult(
                task_id=task.task_id,
                username=task.username,
                status=task.status,
                result=task.result
            ))
    return QueryProgressResponse(tasks=results)

@app.get("/api/tasks/{task_id}/result", response_model=TaskResult)
def get_task_result(task_id: int):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    with task.lock:
        return TaskResult(
            task_id=task.task_id,
            username=task.username,
            status=task.status,
            result=task.result
        )

# 优雅关闭
import atexit
@atexit.register
def shutdown():
    stop_workers()

# FastAPI启动命令（开发调试用）
# uvicorn main:app --reload
