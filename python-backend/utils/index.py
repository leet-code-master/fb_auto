# 浏览器启动需要使用的
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 注册一个谷歌浏览器
def get_chrome_driver(headless=False, incognito=True, executable_path="/usr/local/bin/chromedriver"):
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")  # 启动无头模式

    if incognito:
        chrome_options.add_argument("--incognito")  # 无痕模式（可选）

    service = Service(executable_path=executable_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver