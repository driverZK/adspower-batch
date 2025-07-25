# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_values
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv
import os
import requests
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException 
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


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

# 加载 .env 文件中的环境变量
load_dotenv()


class PostgresDBManager:
    def __init__(self, connection_pool=None):
        """初始化数据库连接或使用连接池"""
        self.connection = None
        self.cursor = None
        self.connection_pool = connection_pool
        try:
            if self.connection_pool:
                self.connection = self.connection_pool.getconn()
            else:
                self.connection = psycopg2.connect(
                    user=os.getenv("DB_USER"),
                    password=os.getenv("DB_PASSWORD"),
                    host=os.getenv("DB_HOST"),
                    port=os.getenv("DB_PORT"),
                    database=os.getenv("DB_NAME")
                )
            self.cursor = self.connection.cursor()
            logger.debug("数据库连接已建立")
        except (Exception, Error) as error:
            logger.error("连接数据库时出错: %s", error)
            raise

    def close_connection(self):
        """关闭数据库连接或归还到连接池"""
        if self.connection:
            if self.cursor:
                self.cursor.close()
            if self.connection_pool:
                self.connection_pool.putconn(self.connection)
            else:
                self.connection.close()
            logger.debug("数据库连接已关闭或归还到连接池")

    def create_email_content_table(self):
        """创建 outlook_email_content 表"""
        try:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS outlook_email_content (
                    id SERIAL PRIMARY KEY,
                    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    email_address VARCHAR(255) NOT NULL,
                    email_title VARCHAR(255),
                    email_content TEXT
                );
            '''
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("表 outlook_email_content 创建成功")
        except (Exception, Error) as error:
            logger.error("创建 outlook_email_content 表时出错: %s", error)
            raise

    def create_email_list_table(self):
        """创建 outlook_email_list 表"""
        try:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS outlook_email_list (
                    id SERIAL PRIMARY KEY,
                    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    address VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    source VARCHAR(255),
                    ads_browser_id VARCHAR(255) UNIQUE,
                    ads_browser_num VARCHAR(255),
                    proxy_ip VARCHAR(255),
                    proxy_country VARCHAR(255),
                    is_valid BOOLEAN DEFAULT TRUE,
                    is_login BOOLEAN DEFAULT FALSE,
                    is_need_check INTEGER DEFAULT 0,
                    need_check_time TIMESTAMP,
                    stop_time TIMESTAMP,
                    remark TEXT
                );
            '''
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("表 outlook_email_list 创建成功")
        except (Exception, Error) as error:
            logger.error("创建 outlook_email_list 表时出错: %s", error)
            raise

    def insert_email_content(self, email_data):
        """批量插入邮件数据到 outlook_email_content 表"""
        try:
            insert_query = '''
                INSERT INTO outlook_email_content (email_address, email_title, email_content)
                VALUES %s;
            '''
            values = [(data['email_address'], data['email_title'], data['email_content']) for data in email_data]
            execute_values(self.cursor, insert_query, values)
            self.connection.commit()
            logger.info("向 outlook_email_content 表插入 %d 条数据成功", len(values))
        except (Exception, Error) as error:
            logger.error("插入 outlook_email_content 数据时出错: %s", error)
            self.connection.rollback()
            raise

    def query_valid_emails(self):
        """查询 is_valid=TRUE, is_login=TRUE, is_need_check>0 的记录"""
        try:
            query = '''
                SELECT address, ads_browser_id
                FROM outlook_email_list
                WHERE is_valid = TRUE AND is_login = TRUE AND is_need_check > 0;
            '''
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logger.info("查询到 %d 条符合条件的邮箱记录", len(rows))
            for row in rows:
                logger.debug("符合条件的邮箱记录: %s", row)
            return [{"address": row[0], "ads_browser_id": row[1]} for row in rows]
        except (Exception, Error) as error:
            logger.error("查询 outlook_email_list 表时出错: %s", error)
            return []

    def query_table(self, table_name):
        """查询指定表的所有数据"""
        try:
            query = f'SELECT * FROM {table_name};'
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            logger.info("从 %s 表查询到 %d 条记录", table_name, len(rows))
            for row in rows:
                logger.debug("%s 表记录: %s", table_name, row)
            return rows
        except (Exception, Error) as error:
            logger.error("查询 %s 表时出错: %s", table_name, error)
            raise

    def update_is_need_check(self, email_address):
        """将指定邮箱的 is_need_check 置为 0"""
        try:
            update_query = '''
                UPDATE outlook_email_list
                SET is_need_check = 0
                WHERE address = %s;
            '''
            self.cursor.execute(update_query, (email_address,))
            self.connection.commit()
            logger.info("邮箱 %s 的 is_need_check 已置为 0", email_address)
        except (Exception, Error) as error:
            logger.error("更新邮箱 %s 的 is_need_check 时出错: %s", email_address, error)
            self.connection.rollback()
            raise



class OutlookEmailFetcher:
    def __init__(self, adspower_api_url="http://local.adspower.net:50325"):
        """初始化 AdsPower API 地址"""
        self.adspower_api_url = adspower_api_url
        logger.info("初始化 OutlookEmailFetcher, AdsPower API 地址: %s", adspower_api_url)

    def fetch_outlook_emails(self, email_address, ads_browser_id):
        """使用 AdsPower 和 Selenium 读取 Outlook 前 3 封非广告邮件"""
        start_url = f"{self.adspower_api_url}/api/v2/browser-profile/start"
        stop_url = f"{self.adspower_api_url}/api/v2/browser-profile/stop"
        emails = []

        try:
            # 启动 AdsPower 指纹浏览器
            start_payload = {"profile_id": ads_browser_id, "proxy_detection": "0"}
            logger.debug("发送启动浏览器请求: %s, 参数: %s", start_url, start_payload)
            resp = requests.post(start_url, json=start_payload).json()
            if resp["code"] != 0:
                logger.error("无法启动 AdsPower 浏览器 %s: %s", ads_browser_id, resp["msg"])
                return emails
            
            logger.info("成功启动 AdsPower 浏览器 %s", ads_browser_id)
            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", resp["data"]["ws"]["selenium"])
            driver = webdriver.Chrome(options=chrome_options)
            driver.maximize_window()
            
            # 访问 Outlook 收件箱
            logger.debug("访问 Outlook 收件箱: %s", email_address)
            driver.get("https://outlook.live.com")

            wait_time = random.uniform(4, 8)
            logger.info(f"随机等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)
            
            try:
                # 等待邮件列表加载
                logger.debug("等待邮件列表加载")
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='listbox'] [role='option']"))
                )
                logger.info("邮件列表加载成功")
                
                # 获取邮件列表，过滤广告邮件
                email_elements = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
                logger.info("找到 %d 封邮件", len(email_elements))
                non_ad_emails = []
                for elem in email_elements:
                    try:
                        # 检查是否为广告邮件
                        is_ad = False
                        # 检查 'Ad' 标签
                        ad_labels = elem.find_elements(By.CSS_SELECTOR, ".m9Rge")
                        if ad_labels and ad_labels[0].text.strip().lower() == "ad":
                            logger.debug("跳过广告邮件，包含 'Ad' 标签")
                            is_ad = True
                        # 检查广告图片
                        ad_images = elem.find_elements(By.CSS_SELECTOR, "img[src*='ads-olk-icon.png']")
                        if ad_images:
                            logger.debug("跳过广告邮件，包含 ads-olk-icon.png")
                            is_ad = True
                        # 检查发件人（可选：排除常见广告发件人）
                        sender = elem.find_elements(By.CSS_SELECTOR, ".ESO13 span")
                        if sender and "microsoft outlook" in sender[0].text.lower():
                            logger.debug("跳过广告邮件，发件人: %s", sender[0].text)
                            is_ad = True
                        if not is_ad:
                            non_ad_emails.append(elem)
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        logger.debug("检查邮件广告标识时出错: %s", e)
                        continue

                logger.info("过滤后找到 %d 封非广告邮件，读取最新 1封", len(non_ad_emails))
                
                # 读取最新1封非广告邮件
                for idx, email_elem in enumerate(non_ad_emails[:1]):
                    try:
                        logger.info("点击第 %d 封非广告邮件", idx + 1)
                        # 获取邮件标题
                        try:
                            title = email_elem.find_element(By.CSS_SELECTOR, "span[title]")
                            email_title = title.text
                            logger.info("提取邮件标题: %s", email_title)
                            title.click()
                            logger.debug("提取邮件标题: %s", email_title)
                        except TimeoutException:
                            logger.error("无法提取第 %d 封邮件标题", idx + 1)
                            email_title = "No title found"
                        
                        wait_time = random.uniform(4, 8)
                        logger.info(f"随机等待 {wait_time:.2f} 秒")
                        time.sleep(wait_time)
                        
                        # 获取邮件内容
                        try:
                            content_elem = WebDriverWait(driver, 8).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='document']"))
                            )
                            email_content = content_elem.text.strip()
                            logger.debug("提取邮件内容: %s", email_content[:150] + "..." if len(email_content) > 50 else email_content)
                        except TimeoutException:
                            logger.error("无法提取第 %d 封邮件内容", idx + 1)
                            email_content = "No content found"
                        
                        emails.append({
                            "email_address": email_address,
                            "email_title": email_title,
                            "email_content": email_content
                        })
                        logger.info("成功读取第 %d 封非广告邮件", idx + 1)
                        
                    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                        logger.error("无法读取第 %d 封非广告邮件: %s", idx + 1, e)
                        continue
                
            except TimeoutException as e:
                logger.error("无法加载 %s 的邮件列表: %s", email_address, e)

            wait_time = random.uniform(4, 10)
            logger.info(f"随机等待 {wait_time:.2f} 秒")
            time.sleep(wait_time)

            # 清理
            driver.quit()
            logger.debug("关闭 Selenium 浏览器")
            logger.debug("发送关闭浏览器请求: %s, %s", stop_url, {"profile_id": ads_browser_id})
            requests.post(stop_url, json={"profile_id": ads_browser_id})
            logger.info("AdsPower 浏览器 %s 已关闭", ads_browser_id)
            return emails
        
        except Exception as e:
            logger.error("处理 AdsPower 浏览器 %s 时出错: %s", ads_browser_id, e)
            logger.debug("发送关闭浏览器请求: %s, %s", stop_url, {"profile_id": ads_browser_id})
            requests.post(stop_url, json={"profile_id": ads_browser_id})
            return emails


def process_email_task(email, downloader, connection_pool):
    """处理单个邮箱账户，读取邮件并存储到数据库"""
    db_manager = PostgresDBManager(connection_pool=connection_pool)
    try:
        logger.info("处理邮箱: %s, AdsPower ID: %s", email['address'], email['ads_browser_id'])
        emails = downloader.fetch_outlook_emails(email['address'], email['ads_browser_id'])
        if emails:
            logger.info("为 %s 读取到 %d 封邮件", email['address'], len(emails))
            db_manager.insert_email_content(emails)
            logger.info("更新邮箱 %s 的 is_need_check", email['address'])
            db_manager.update_is_need_check(email['address'])
        else:
            logger.warning("为 %s 未读取到邮件", email['address'])
    except Exception as e:
        logger.error("处理邮箱 %s 时出错: %s", email['address'], e)
    finally:
        db_manager.close_connection()

def main_loop(polling_interval=60, max_workers=5):
    """主循环，持续监控并并发处理邮件"""
    logger.info("启动主循环，轮询间隔 %d 秒，最大并发数 %d", polling_interval, max_workers)
    connection_pool = ThreadedConnectionPool(
        minconn=1,
        maxconn=max_workers,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME")
    )
    db_manager = PostgresDBManager(connection_pool=connection_pool)
    downloader = OutlookEmailFetcher()

    try:
        while True:
            try:
                # 查询符合条件的邮箱
                logger.info("查询符合条件的邮箱记录")
                valid_emails = db_manager.query_valid_emails()
                if not valid_emails:
                    logger.info("未找到符合条件的邮箱，等待下次轮询")
                    time.sleep(polling_interval)
                    continue

                # 并发处理邮箱
                logger.info("开始并发处理 %d 个邮箱", len(valid_emails))
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [
                        executor.submit(process_email_task, email, downloader, connection_pool)
                        for email in valid_emails
                    ]
                    for future in as_completed(futures):
                        try:
                            future.result()
                        except Exception as e:
                            logger.error("并发任务出错: %s", e)

                logger.info("完成一批处理，等待 %d 秒", polling_interval)
                time.sleep(polling_interval)

            except Exception as e:
                logger.error("主循环迭代出错: %s", e)
                time.sleep(polling_interval)

    except KeyboardInterrupt:
        logger.info("收到 KeyboardInterrupt, 程序关闭")
    except Exception as e:
        logger.error("主循环致命错误: %s", e)
    finally:
        db_manager.close_connection()
        connection_pool.closeall()
        logger.info("连接池已关闭，程序终止")

# 示例用法
if __name__ == "__main__":
    logger.info("程序启动")
    main_loop(polling_interval=60, max_workers=5)
    """
    logger.info("程序启动")
    try:
        # 初始化数据库和邮件获取器
        db_manager = PostgresDBManager()
        email_fetcher = OutlookEmailFetcher()

        # 创建表
        logger.info("开始创建数据库表")
        # db_manager.create_email_content_table()
        # db_manager.create_email_list_table()

        # 处理符合条件的邮箱
        logger.info("查询符合条件的邮箱列表")
        valid_emails = db_manager.query_valid_emails()
        for email in valid_emails:
            logger.info("处理邮箱: %s, AdsPower ID: %s", email['address'], email['ads_browser_id'])
            emails = email_fetcher.fetch_outlook_emails(email['address'], email['ads_browser_id'])
            if emails:
                logger.info("读取到 %d 封非广告邮件，插入数据库", len(emails))
                db_manager.insert_email_content(emails)
                logger.info("更新邮箱 %s 的 is_need_check", email['address'])
                db_manager.update_is_need_check(email['address'])
        # 查询结果
        logger.info("查询 outlook_email_content 表结果")
        db_manager.query_table("outlook_email_content")

    except Exception as e:
        logger.error("程序执行出错: %s", e)
    finally:
        # 关闭数据库连接
        logger.info("关闭数据库连接")
        db_manager.close_connection()
        logger.info("程序结束")
    """