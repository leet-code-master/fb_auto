import time
import threading
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException
)
import os
CHROMEDRIVER_PATH = r'static\chromedriver.exe'

print(f"CHROMEDRIVER_PATH={CHROMEDRIVER_PATH}")
print(f"File exists: {os.path.exists(CHROMEDRIVER_PATH)}")
print(f"Is executable: {os.access(CHROMEDRIVER_PATH, os.X_OK)}")

# ===================== 页面常量 =====================

FACEBOOK_LOGIN_URL = "https://www.facebook.com/login"
FACEBOOK_EMAIL_INPUT = (By.ID, "email")
FACEBOOK_PASSWORD_INPUT = (By.ID, "pass")
FACEBOOK_LOGIN_BUTTON = (By.NAME, "login")
FACEBOOK_2FA_INPUTS = [
    (By.ID, "approvals_code"),
    (By.NAME, "approvals_code"),
]
FACEBOOK_2FA_SUBMIT_BUTTONS = [
    (By.ID, "checkpointSubmitButton"),
    (By.NAME, "checkpointSubmitButton"),
]
FACEBOOK_HOME_URL = "https://www.facebook.com/me"
FACEBOOK_PROFILE_NAME_SELECTOR = (By.CSS_SELECTOR, '[data-testid="profile_name_in_profile_page"]')
FACEBOOK_SECURITY_SETTINGS_URL = "https://www.facebook.com/settings?tab=security"


# ===================== 各种登录流程情况处理器 =====================

class BaseLoginStep:
    def match(self, driver):
        raise NotImplementedError

    def handle(self, driver, account_info):
        raise NotImplementedError


class PasswordErrorStep(BaseLoginStep):
    def match(self, driver):
        page = driver.page_source
        return (
                "账号密码错误" in page or
                "The password that you've entered is incorrect" in page
        )

    def handle(self, driver, account_info):
        return {"success": False, "error": "账号或密码错误"}


class TwoFAStep(BaseLoginStep):
    def match(self, driver):
        page = driver.page_source
        return (
                "Enter security code" in page or
                "请输入安全码" in page or
                "Two-factor authentication required" in page
        )

    def handle(self, driver, account_info):
        try:
            driver.switch_to.new_window('tab')
            try:
                code = fetch_2fa_code(account_info)
            except Exception as e:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                return {"success": False, "error": f"获取二步验证码失败: {str(e)}"}
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            # 填写验证码
            input_found = False
            for by, value in FACEBOOK_2FA_INPUTS:
                try:
                    driver.find_element(by, value).send_keys(code)
                    input_found = True
                    break
                except Exception:
                    continue
            if not input_found:
                return {"success": False, "error": "未找到验证码输入框"}
            # 提交按钮
            btn_found = False
            for by, value in FACEBOOK_2FA_SUBMIT_BUTTONS:
                try:
                    driver.find_element(by, value).click()
                    btn_found = True
                    break
                except Exception:
                    continue
            if not btn_found:
                return {"success": False, "error": "未找到验证码提交按钮"}
            time.sleep(2)
            page = driver.page_source
            if "验证码错误" in page or "incorrect code" in page:
                return {"success": False, "error": "双重验证码错误"}
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"二步验证处理异常: {str(e)}"}


class LoginSuccessStep(BaseLoginStep):
    def match(self, driver):
        title = driver.title
        return ("Facebook" in title and "登录" not in title) or "主页" in driver.page_source

    def handle(self, driver, account_info):
        return {"success": True}


def fetch_2fa_code(account_info):
    raise NotImplementedError("请实现 fetch_2fa_code 逻辑！")


LOGIN_STEPS = [
    PasswordErrorStep(),
    TwoFAStep(),
    LoginSuccessStep()
]


# === execution_modules 各模块的具体处理函数 ===
def module_1_action(driver, account_info):
    try:
        driver.get(FACEBOOK_HOME_URL)
        time.sleep(2)
        user_name = None
        try:
            user_name = driver.find_element(*FACEBOOK_PROFILE_NAME_SELECTOR).text
        except Exception:
            pass
        return {"success": True, "module": 1, "user_name": user_name or "未知"}
    except Exception as e:
        return {"success": False, "module": 1, "error": str(e)}


def module_2_action(driver, account_info):
    try:
        driver.get(FACEBOOK_SECURITY_SETTINGS_URL)
        time.sleep(2)
        # ...实际操作省略
        return {"success": True, "module": 2, "msg": "密码修改操作完成（示例）"}
    except Exception as e:
        return {"success": False, "module": 2, "error": str(e)}


MODULE_ACTIONS = {
    1: module_1_action,
    2: module_2_action
}


def login_facebook_with_steps(driver, account_info, execution_modules, task_id=None, save_thread_id_func=None):
    try:
        driver.get(FACEBOOK_LOGIN_URL)
    except TimeoutException:
        return {"success": False, "error": "Facebook 登录页打开超时"}
    except WebDriverException as e:
        return {"success": False, "error": f"无法打开Facebook登录页: {e}"}
    time.sleep(2)

    try:
        driver.find_element(*FACEBOOK_EMAIL_INPUT).send_keys(account_info['username'])
        driver.find_element(*FACEBOOK_PASSWORD_INPUT).send_keys(account_info['password'])
        driver.find_element(*FACEBOOK_LOGIN_BUTTON).click()
    except NoSuchElementException:
        return {"success": False, "error": "找不到登录表单，请检查页面结构"}
    except Exception as e:
        return {"success": False, "error": f"账号密码输入异常: {e}"}
    time.sleep(3)

    # 在首次进入worker时写入thread_id
    if task_id is not None and save_thread_id_func:
        try:
            thread_id = threading.get_ident()
            save_thread_id_func(task_id, thread_id)
        except Exception:
            pass

    for step in LOGIN_STEPS:
        try:
            if step.match(driver):
                result = step.handle(driver, account_info)
                if not result.get("success", False):
                    return result
        except Exception as e:
            return {"success": False, "error": f"执行步骤{step.__class__.__name__}异常: {e}"}

    module_results = []
    for mod in execution_modules or []:
        action_func = MODULE_ACTIONS.get(mod)
        if action_func:
            try:
                mod_result = action_func(driver, account_info)
            except Exception as e:
                mod_result = {"success": False, "module": mod, "error": str(e)}
            module_results.append(mod_result)
        else:
            module_results.append({"success": False, "module": mod, "error": f"未知模块:{mod}"})

    return {
        "success": True,
        "modules_completed": module_results
    }


def login_facebook(account_info, execution_modules=None, is_headless=True, task_id=None, save_thread_id_func=None):
    options = Options()
    if is_headless:
        options.add_argument('--headless=new')
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    driver = None
    try:
        service = ChromeService(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        result = login_facebook_with_steps(
            driver,
            account_info,
            execution_modules or [],
            task_id=task_id,
            save_thread_id_func=save_thread_id_func
        )
        return result
    except Exception as e:
        return {"success": False, "error": f"浏览器异常: {str(e)}"}
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        try:
            import psutil
            this_proc = psutil.Process(os.getpid())
            for child in this_proc.children(recursive=True):
                name = child.name().lower()
                if 'chrome' in name or 'chromedriver' in name:
                    child.kill()
        except Exception:
            pass
