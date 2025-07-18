from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import requests

# 配置 AdsPower WebDriver
ads_power_webdriver_url = "http://local.adspower.net:50325/api/v2/browser-profile/start"

def get_ads_browser(profile_id):
    """
    用API查询ads浏览器环境
    """
    param = {
        "profile_id": str(profile_id),
        "proxy_detection": "0",
        "headless": "0"
    }
    res = requests.post(ads_power_webdriver_url, json=param)
    ads_data = res.json()
    print(ads_data)
    sel = ads_data['data']['ws']['selenium']

    return sel

options = Options()

profile_id = "k11wlalv"
debuggerAddress = get_ads_browser(profile_id)
print(debuggerAddress)

options.add_experimental_option("debuggerAddress", debuggerAddress)  # 从 API 返回的地址

driver = webdriver.Chrome(options=options)

try:
    driver.get("https://outlook.live.com/mail/inbox")
    time.sleep(15)

    email_lists = driver.find_element(By.CSS_SELECTOR, 'div[data-animatable="true"]')
    if not email_lists:
        print(email_lists)
    else:
        latest_email = email_lists[0]
        subject = latest_email.find_element(By.CSS_SELECTOR, "span[title]").text

        latest_email.click()
        time.sleep(5)

        content = driver.find_element(By.CSS_SELECTOR, "div[role='document']").text
        print(f"Subject: {subject}\nContent: {content}")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()
