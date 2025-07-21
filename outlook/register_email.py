import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException
import sys
import random
import string
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# AdsPower API 配置
ads_id = "k11yv3h0"  # 替换为您的 AdsPower 用户 ID
open_url = "http://local.adspower.net:50325/api/v2/browser-profile/start"
close_url = "http://local.adspower.net:50325/api/v2/browser-profile/start"

# 获取 AdsPower 浏览器实例
param = {"profile_id": str(ads_id), "proxy_detection": "0", "headless": "0"}
resp = requests.post(open_url, json=param).json()
if resp["code"] != 0:
    print(resp["msg"])
    print("请检查 ads_id 是否正确")
    sys.exit()

print(resp)
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# 生成随机邮箱和密码
def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# username = generate_random_string(10) + "@outlook.com"
# username = generate_random_string(10) + "yang"
# password = "B_" + generate_random_string(6) + "123789"

username = "crazykooper992"
password = "B_xtroni123789"

try:
    # 打开 Outlook 页
    driver.get("https://outlook.live.com")

    time.sleep(5)

    # 打开 Outlook 注册页面
    driver.get("https://go.microsoft.com/fwlink/p/?linkid=2125440&clcid=0x409&culture=en-us")
    
    # 等待页面加载
    wait = WebDriverWait(driver, 10)
    
    # 检查是否存在个人数据导出许可弹窗（英文页面）
    try:
        # 匹配英文“Accept”或“Accept and Continue”按钮
        accept_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Accept and Continue')]")))
        accept_button.click()
        print("Clicked 'Accept' or 'Accept and Continue' button")
    except Exception as e:
        print("No Pop found, proceeding with registration")
    
    # 输入邮箱
    email_input = wait.until(EC.presence_of_element_located((By.ID, "floatingLabelInput6")))
    time.sleep(random.uniform(3.9, 6.5))
    email_input.send_keys(username)

    print("username:", username)
    
    # 点击“Next”按钮
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    time.sleep(random.uniform(2.9, 5.9))
    next_button.click()
    
    # 输入密码
    # 方案一
    # password_input = wait.until(EC.presence_of_element_located((By.ID, "floatingLabelInput44")))
    # 方案二
    password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="new-password"]')))
    time.sleep(random.uniform(4.9, 7.5))
    password_input.send_keys(password)

    print("password:", password)
    
    # 点击“Next”按钮
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    time.sleep(random.uniform(2.9, 5.5))
    next_button.click()
    
    time.sleep(5)
    # 等待跳转到出生年月日页面
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'BirthMonthDropdown')))
        logger.info("Birth date page loaded with BirthMonthDropdown present")
        WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
        logger.info("Birth date page readyState: complete")
    except TimeoutException:
        logger.error("Failed to load birth date page")
        raise

    # 检查并隐藏防机器人 iframe
    try:
        driver.execute_script("""
            let iframes = document.querySelectorAll('iframe[data-testid="deviceFingerPrinting"], iframe[data-testid="humanIframe"]');
            iframes.forEach(iframe => {
                iframe.style.display = 'none';
                iframe.setAttribute('aria-hidden', 'true');
            });
        """)
        logger.info("Hid DeviceFingerPrinting and Human Iframe to bypass bot detection")
    except:
        logger.warning("Failed to hide iframes, continuing...")
    
    # 确保在主上下文
    driver.switch_to.default_content()
    logger.info("Switched to default content")

    # ==================== 选择月份 BirthMonth =======================
    months_list = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    target_month = random.choice(months_list)
    try:
        month_button = wait.until(EC.element_to_be_clickable((By.ID, 'BirthMonthDropdown')))

        logger.info("BirthMonthDropdown located")

        # 滚动到按钮并模拟用户行为
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", month_button)
        time.sleep(random.uniform(0.5, 1.5))
        
        # 尝试 ActionChains 点击
        actions = ActionChains(driver)
        actions.move_to_element(month_button).pause(random.uniform(1.2, 2.5)).click().perform()
        logger.info("Clicked BirthMonthDropdown with ActionChains")
        
        # 等待 aria-expanded="true"
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[@id='BirthMonthDropdown' and @aria-expanded='true']")))
        logger.info("BirthMonthDropdown expanded")

        # 获取 aria-owns 属性, 
        # possible_ids = ["fluent-listbox24", "fluent-listbox980"]
        month_listbox_id = "fluent-listbox24"
        # 等待月份选项列表可见
        month_options_container = wait.until(EC.visibility_of_element_located((By.ID, month_listbox_id)))
        logger.info("Month options container visible")

        # 选择目标月份
        month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//div[@id='{month_listbox_id}']//div[@role='option' and contains(text(), '{target_month}')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", month_option)
        time.sleep(random.uniform(3.8, 7.5))
        month_option.click()
        logger.info(f"Selected month: {target_month}")
        time.sleep(0.8)
    except WebDriverException as e:
        logger.error(f"Error selecting month: {str(e)}")
        raise
    
    # ==================== 选择日期 BirthDay =======================
    target_day = str(random.randint(1, 30))
    try:
        day_button = wait.until(EC.element_to_be_clickable((By.ID, 'BirthDayDropdown')))

        logger.info("BirthDayDropdown located")

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", day_button)

        time.sleep(1.5)  # 等待滚动完成
    
        # 使用 JavaScript 点击日期按钮
        driver.execute_script("arguments[0].click();", day_button)

        time.sleep(random.uniform(2.8, 5.5))
    
        # 动态获取日期选项列表 ID
        day_listbox_id = "fluent-listbox25"
        day_options_container = wait.until(EC.visibility_of_element_located((By.ID, day_listbox_id)))
    
        # 选择目标日期
        day_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//div[@id='{day_listbox_id}']//div[@role='option' and contains(text(), '{target_day}')]"))
        )
        time.sleep(random.uniform(2.9, 5.5))
        day_option.click()
        time.sleep(1)
    except Exception as e:
        logger.error(f"Error selecting day: {str(e)}")
        raise

    # 填写年份
    target_year = str(random.randint(1972, 2005))
    birth_year = driver.find_element(By.CSS_SELECTOR, 'input[name="BirthYear"]')
    time.sleep(random.uniform(0.9, 2.5))
    birth_year.send_keys(target_year)
    time.sleep(3)
    
    # 点击“Next”按钮
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    next_button.click()

    time.sleep(3.8)
    # 输入姓名（示例：随机生成）
    first_name = wait.until(EC.presence_of_element_located((By.ID, "firstNameInput")))
    time.sleep(random.uniform(1.5, 3.5))
    first_name.send_keys(generate_random_string(8))
    
    print("first_name:", first_name)
    time.sleep(2.2)
    
    last_name = driver.find_element(By.ID, "lastNameInput")
    time.sleep(random.uniform(1.9, 4.5))
    last_name.send_keys(generate_random_string(6))

    print("last_name:", last_name)
    time.sleep(1.3)
    
    # 点击“Next”按钮
    next_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    next_button.click()
    
    # 等待注册完成页面加载
    time.sleep(5)
    
    # 模拟真人验证：点击固定按钮并保持直到进度条完成
    try:
        time.sleep(2)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'prove')]")))
        logger.info("Human verification page loaded")

        # 切换到第一层 iframe
        captcha_iframe = wait.until(EC.presence_of_element_located((By.XPATH, "//iframe[@title='Verification challenge']")))
        driver.switch_to.frame(captcha_iframe)
        logger.info("Switched to first iframe: Verification challenge")

        # 等待 px-captcha 容器加载
        try:
            wait.until(EC.presence_of_element_located((By.ID, "px-captcha"))) 
            logger.info("定位到 px-captcha 容器")
        except Exception as e:
            logger.error(f"未找到 px-captcha 容器: {str(e)}")
            raise
        
        # 优先尝试 Shadow DOM 内显示的 iframe
        try:
            nested_iframe = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//iframe[@title='Human verification challenge' and contains(@style, 'display: block')]"))
            )
            logger.info("定位到 Shadow DOM内的嵌套的第二层 iframe: Human verification challenge")
            driver.switch_to.frame(nested_iframe)
            logger.info("Switched to second iframe: Human verification challenge")

            captcha_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//p[contains(text(), 'Press & Hold')]")))
        except Exception as e:
            logger.error(f"未找到 captcha_button: {str(e)}")
            raise

        if not captcha_button:
            logger.error(f"未找到 captcha_button: {str(e)}")
            raise
        else:
            # 模拟按住5-8秒
            actions = ActionChains(driver)
            actions.move_by_offset(random.randint(10, 50), random.randint(10, 50)).pause(random.uniform(0.3, 0.7))
            actions.move_to_element(captcha_button).pause(random.uniform(0.5, 1.0))
            actions.click_and_hold().pause(random.uniform(5, 8)).release().perform()
            logger.info("Pressed and held CAPTCHA <p> element for 5-7 seconds")
        
        # 切换回默认上下文
        driver.switch_to.default_content()
        logger.info("已切换回默认上下文")

        print("Human verification completed: Button held until progress bar finished")
    except Exception as e:
        print(f"Human verification failed: {str(e)}")
        print("Please check the verification button or progress bar element ID")
        raise

    time.sleep(5)

    # 按钮<Skip for now> Sign in faster with your face, fingerprint, or PIN
    skip_for_now_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="secondaryButton"]')
    skip_for_now_button.click()

    time.sleep(5)

    # 按钮<Skip for now> Sign in faster with your face, fingerprint, or PIN
    # Create a passkey to sign in to your Microsoft account. No passwords, apps, or codes needed.
    skip_for_now_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="secondaryButton"]')
    skip_for_now_button.click()

    time.sleep(5)

    print(f"Registration successful! Email: {username}, Password: {password}")

except Exception as e:
    print(f"Error during registration: {str(e)}")

finally:
    # 关闭浏览器
    driver.quit()
    requests.get(close_url)