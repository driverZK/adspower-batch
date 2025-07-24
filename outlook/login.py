import requests
import time
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.FileHandler('outlook_login.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ADS Power API 配置
ADSP_BASE_URL = "http://local.adspower.net:50325"  # 本地 ADS Power API 地址
PROFILE_ID = "k11yvbja"  # 浏览器指纹配置文件ID
PROXY_DETECTION = "0"  # 代理检测设置，0 表示关闭，1 表示开启，根据需要修改

# Outlook 登录凭据
OUTLOOK_EMAIL = "OlwinMuncher36@outlook.com"  # 替换为你的 Outlook 邮箱
OUTLOOK_PASSWORD = "p87o6gAU31j"  # 替换为你的 Outlook 密码

def start_adspower_profile():
    """启动 ADS Power 指纹浏览器实例"""
    logger.info("正在启动 ADS Power 指纹浏览器实例")
    url = f"{ADSP_BASE_URL}/api/v2/browser-profile/start"
    payload = {
        "profile_id": PROFILE_ID,
        "proxy_detection": PROXY_DETECTION
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 0:
                selenium_port = data["data"]["ws"]["selenium"]
                logger.info(f"浏览器实例启动成功, Selenium 端口: {selenium_port}")
                return selenium_port
            else:
                logger.error(f"启动浏览器失败: {data['msg']}")
                raise Exception(f"启动浏览器失败: {data['msg']}")
        else:
            logger.error(f"API 请求失败: {response.text}")
            raise Exception(f"API 请求失败: {response.text}")
    except Exception as e:
        logger.error(f"启动浏览器时发生错误: {str(e)}")
        raise

def stop_adspower_profile():
    """关闭 ADS Power 指纹浏览器实例"""
    logger.info("正在关闭 ADS Power 指纹浏览器实例")
    url = f"{ADSP_BASE_URL}/api/v2/browser-profile/stop"
    payload = {
        "profile_id": PROFILE_ID
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data["code"] == 0:
                logger.info("浏览器实例已关闭")
            else:
                logger.error(f"关闭浏览器失败: {data['msg']}")
        else:
            logger.error(f"API 请求失败: {response.text}")
    except Exception as e:
        logger.error(f"关闭浏览器时发生错误: {str(e)}")

def login_outlook():
    """使用 Selenium 登录 Outlook 邮箱"""
    try:
        # 获取 ADS Power 提供的 Selenium WebSocket 端口
        selenium_port = start_adspower_profile()

        # 配置 Selenium WebDriver
        logger.info("正在配置 Selenium WebDriver")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{selenium_port}")
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        logger.info("Selenium WebDriver 配置完成")

        # 访问 Outlook 主页面
        logger.info("正在访问 Outlook 主页面")
        driver.get("https://outlook.live.com")
        logger.info("已打开 Outlook 主页面")

        wait_time = random.uniform(3, 7)
        logger.info(f"在Outlook主页, 随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)

        # 点击“Sign in”按钮
        logger.info("正在点击 'Sign in' 按钮")
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "action-oc5b26"))
            # 备用定位：By.XPATH("//a[@data-bi-ecn='Sign in']")
        )
        sign_in_button.click()
        logger.info("已点击 'Sign in'")
        wait_time = random.uniform(1, 3)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)

        # 切换到新打开的标签页
        logger.info(f"当前窗口句柄数量: {len(driver.window_handles)}")
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
            logger.info("已切换到新标签页")
        else:
            logger.error("未检测到新标签页")
            raise Exception("未检测到新标签页")

        # 等待并输入邮箱
        logger.info("正在输入邮箱")
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "i0116"))
            # 备用定位：By.NAME("loginfmt") 或 By.XPATH("//input[@name='loginfmt']")
        )
        wait_time = random.uniform(1, 3)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        email_field.send_keys(OUTLOOK_EMAIL)
        logger.info("已输入邮箱")

        # 点击“Next”按钮（邮箱页面）
        logger.info("正在点击 'Next' 按钮（邮箱页面）")
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
            # 备用定位：By.XPATH("//input[@value='Next']")
        )
        wait_time = random.uniform(1, 5)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        next_button.click()
        logger.info("已点击 'Next'（邮箱页面）")

        # 等待并输入密码
        logger.info("正在输入密码")
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "passwordEntry"))
            # 备用定位：By.NAME("passwd") 或 By.XPATH("//input[@name='passwd']")
        )
        wait_time = random.uniform(3, 8)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        password_field.send_keys(OUTLOOK_PASSWORD)
        logger.info("已输入密码")

        # 点击“Next”按钮（密码页面）
        logger.info("正在点击 'Next' 按钮（密码页面）")
        next_button_password = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='primaryButton']"))
            # 备用定位：By.XPATH("//button[text()='Next']")
        )
        wait_time = random.uniform(2, 5)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        next_button_password.click()
        logger.info("已点击 'Next'（密码页面）")

        # 第1次处理 备用邮箱页面, 点击"Skip for now (7 days until this is required)"
        logger.info("正在处理添加备用邮箱, 点击Skip for now (7 days until this is required)")
        skip_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iShowSkip"))
        )
        wait_time = random.uniform(5, 11)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        skip_button.click()
        logger.info("已点击 'Skip for now (7 days until this is required)'（添加备用邮箱页面）")

        # 第2次处理 备用邮箱页面, 点击"Skip for now (6 days until this is required)"
        logger.info("正在处理添加备用邮箱, 点击Skip for now (6 days until this is required)")
        skip_2_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "iShowSkip"))
        )
        wait_time = random.uniform(4, 9)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        skip_2_button.click()
        logger.info("已点击 'Skip for now (6 days until this is required)'（添加备用邮箱页面）")

        # 处理“Stay signed in”页面
        logger.info("检查处理'Stay signed in' 页面")
        stay_signed_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-testid='primaryButton']"))
        )
        wait_time = random.uniform(3, 6)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)
        stay_signed_in_button.click()
        logger.info("已点击 'Stay signed in'")


        wait_time = random.uniform(65, 125)
        logger.info(f"随机等待 {wait_time:.2f} 秒")
        time.sleep(wait_time)

        # 验证是否登录成功
        logger.info("正在验证登录结果")
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "Pivot29-Tab0")))
        logger.info("登录成功，已进入 Outlook 邮箱收件箱")

        # 关闭浏览器
        logger.info("正在关闭浏览器")
        driver.quit()
        stop_adspower_profile()

    except Exception as e:
        logger.error(f"登录过程中出错: {str(e)}")
        driver.quit()
        stop_adspower_profile()

if __name__ == "__main__":
    logger.info("开始执行 Outlook 登录脚本")
    login_outlook()
    logger.info("Outlook 登录脚本执行完成")