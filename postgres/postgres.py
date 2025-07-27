import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

class PostgresDBManager:
    def __init__(self):
        """初始化数据库连接"""
        self.connection = None
        self.cursor = None
        try:
            self.connection = psycopg2.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                database=os.getenv("DB_NAME")
            )
            self.cursor = self.connection.cursor()
            print("数据库连接成功")
        except (Exception, Error) as error:
            print("连接数据库时出错:", error)

    def close_connection(self):
        """关闭数据库连接"""
        if self.connection:
            if self.cursor:
                self.cursor.close()
            self.connection.close()
            print("数据库连接已关闭")

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
            print("表 outlook_email_content 创建成功")
        except (Exception, Error) as error:
            print("创建 outlook_email_content 表时出错:", error)

    def create_email_list_table(self):
        """创建 outlook_email_list 表，address 和 ads_browser_id 唯一，包含 is_need_check 和 need_check_time"""
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
            print("表 outlook_email_list 创建成功")
        except (Exception, Error) as error:
            print("创建 outlook_email_list 表时出错:", error)

    def insert_email_content(self, email_address, email_title, email_content):
        """向 outlook_email_content 表插入数据"""
        try:
            insert_query = '''
                INSERT INTO outlook_email_content (email_address, email_title, email_content)
                VALUES (%s, %s, %s);
            '''
            self.cursor.execute(insert_query, (email_address, email_title, email_content))
            self.connection.commit()
            print("outlook_email_content 表插入数据成功")
        except (Exception, Error) as error:
            print("插入 outlook_email_content 数据时出错:", error)

    def insert_email_list(self, address, password, source=None, ads_browser_id=None, 
                         ads_browser_num=None, proxy_ip=None, proxy_country=None, 
                         is_valid=True, is_login=False, is_need_check=0, 
                         need_check_time=None, stop_time=None, remark=None):
        """向 outlook_email_list 表插入数据，包含 is_need_check 和 need_check_time"""
        try:
            insert_query = '''
                INSERT INTO outlook_email_list (
                    address, password, source, ads_browser_id, ads_browser_num,
                    proxy_ip, proxy_country, is_valid, is_login, is_need_check,
                    need_check_time, stop_time, remark
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            '''
            self.cursor.execute(insert_query, (
                address, password, source, ads_browser_id, ads_browser_num,
                proxy_ip, proxy_country, is_valid, is_login, is_need_check,
                need_check_time, stop_time, remark
            ))
            self.connection.commit()
            print("outlook_email_list 表插入数据成功")
        except (Exception, Error) as error:
            print("插入 outlook_email_list 数据时出错:", error)
    
    def insert_email_list_batch(self, data_list):
        """向 outlook_email_list 表批量插入数据，支持单条或多条"""
        try:
            insert_query = '''
                INSERT INTO outlook_email_list (
                    address, password, source, ads_browser_id, ads_browser_num,
                    proxy_ip, proxy_country, is_valid, is_login, is_need_check,
                    need_check_time, stop_time, remark
                )
                VALUES %s;
            '''
            # 确保 data_list 是列表，即使传入单条数据
            if not isinstance(data_list, list):
                data_list = [data_list]
            
            # 转换为元组列表以供 execute_values 使用
            values = [
                (
                    data.get('address').lower(), data.get('password'), data.get('source'),
                    data.get('ads_browser_id'), data.get('ads_browser_num'),
                    data.get('proxy_ip'), data.get('proxy_country'),
                    data.get('is_valid', True), data.get('is_login', False),
                    data.get('is_need_check', 0), data.get('need_check_time'),
                    data.get('stop_time'), data.get('remark')
                )
                for data in data_list
            ]
            
            execute_values(self.cursor, insert_query, values)
            self.connection.commit()
            print(f"outlook_email_list 表插入 {len(values)} 条数据成功")
        except (Exception, Error) as error:
            print("插入 outlook_email_list 数据时出错:", error)
            self.connection.rollback()

    def query_table(self, table_name):
        """查询指定表的所有数据"""
        try:
            query = f'SELECT * FROM {table_name};'
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            print(f"{table_name} 表查询结果:")
            for row in rows:
                print(row)
            return rows
        except (Exception, Error) as error:
            print(f"查询 {table_name} 表时出错:", error)
            return []

    def alter_email_content_table(self, column_name, column_type, constraint=None):
        """修改 outlook_email_content 表，添加新列"""
        try:
            alter_query = f'''
                ALTER TABLE outlook_email_content
                ADD COLUMN {column_name} {column_type} {constraint if constraint else ''};
            '''
            self.cursor.execute(alter_query)
            self.connection.commit()
            print(f"outlook_email_content 表添加列 {column_name} 成功")
        except (Exception, Error) as error:
            print(f"修改 outlook_email_content 表时出错:", error)

    def alter_email_list_table(self, column_name, column_type, constraint=None):
        """修改 outlook_email_list 表，添加新列"""
        try:
            alter_query = f'''
                ALTER TABLE outlook_email_list
                ADD COLUMN {column_name} {column_type} {constraint if constraint else ''};
            '''
            self.cursor.execute(alter_query)
            self.connection.commit()
            print(f"outlook_email_list 表添加列 {column_name} 成功")
        except (Exception, Error) as error:
            print(f"修改 outlook_email_list 表时出错:", error)

def get_test_data():
    return [
        {
            "address": "KoppenRosenwinkel27@outlook.com",
            "password": "C902NTVv4",
            "source": "manual",
            "ads_browser_id": "k11yvflt",
            "ads_browser_num": "num_001",
            "proxy_ip": "192.168.1.1",
            "proxy_country": "US",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 16:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "PrialAbair013@outlook.com",
            "password": "RK0608badlq6",
            "source": "api",
            "ads_browser_id": "k11yvdfl",
            "ads_browser_num": "num_002",
            "proxy_ip": "192.168.1.2",
            "proxy_country": "UK",
            "is_valid": False,
            "is_login": True,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": "2025-07-26 16:00:00",
            "remark": "account"
        },
        {
            "address": "OlwinMuncher36@outlook.com",
            "password": "p87o6gAU31j",
            "source": "import",
            "ads_browser_id": "k11yvbja",
            "ads_browser_num": "num_003",
            "proxy_ip": "192.168.1.3",
            "proxy_country": "CN",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 17:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "QuealMcniff7779@outlook.com",
            "password": "0n7dU16q143",
            "source": "manual",
            "ads_browser_id": "k11yv68b",
            "ads_browser_num": "num_004",
            "proxy_ip": "192.168.1.4",
            "proxy_country": "JP",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "DeninnoTrotochaud62@outlook.com",
            "password": "i0592F084F",
            "source": "api",
            "ads_browser_id": "k11yv3h0",
            "ads_browser_num": "num_005",
            "proxy_ip": "192.168.1.5",
            "proxy_country": "DE",
            "is_valid": False,
            "is_login": False,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 18:00:00",
            "stop_time": "2025-07-26 18:00:00",
            "remark": "account"
        },
        {
            "address": "KannardJunkin83@outlook.com",
            "password": "Q9pa1Eka38",
            "source": "import",
            "ads_browser_id": "k12a62k5",
            "ads_browser_num": "num_006",
            "proxy_ip": "192.168.1.6",
            "proxy_country": "US",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "JavellanaSak768@outlook.com",
            "password": "2SJEv3FC",
            "source": "manual",
            "ads_browser_id": "k12a66n0",
            "ads_browser_num": "num_007",
            "proxy_ip": "192.168.1.7",
            "proxy_country": "UK",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 19:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "InfantolinoBendle05@outlook.com",
            "password": "88D59YEHM92",
            "source": "api",
            "ads_browser_id": "k12a6868",
            "ads_browser_num": "num_008",
            "proxy_ip": "192.168.1.8",
            "proxy_country": "CN",
            "is_valid": False,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": "2025-07-26 19:00:00",
            "remark": "account"
        },
        {
            "address": "DiesWeaver887@outlook.com",
            "password": "8vLqK6nT",
            "source": "import",
            "ads_browser_id": "k12a69r9",
            "ads_browser_num": "num_009",
            "proxy_ip": "192.168.1.9",
            "proxy_country": "JP",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 20:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "VbilesCaney0167@outlook.com",
            "password": "p5T6x5Rr322",
            "source": "manual",
            "ads_browser_id": "k12a6b4p",
            "ads_browser_num": "num_010",
            "proxy_ip": "192.168.1.10",
            "proxy_country": "DE",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "HertleinSizemore8714@outlook.com",
            "password": "yHVLJ7xSe20",
            "source": "api",
            "ads_browser_id": "k12a6cbm",
            "ads_browser_num": "num_011",
            "proxy_ip": "192.168.1.11",
            "proxy_country": "US",
            "is_valid": False,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 21:00:00",
            "stop_time": "2025-07-26 21:00:00",
            "remark": "account"
        },
        {
            "address": "VirgelBraughton62@outlook.com",
            "password": "x521QuD2S72k",
            "source": "import",
            "ads_browser_id": "k12a6fc9",
            "ads_browser_num": "num_012",
            "proxy_ip": "192.168.1.12",
            "proxy_country": "UK",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "LachappelleSmall7389@outlook.com",
            "password": "mR76qq34",
            "source": "manual",
            "ads_browser_id": "k12a6fcb",
            "ads_browser_num": "num_013",
            "proxy_ip": "192.168.1.13",
            "proxy_country": "CN",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 22:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "MatsuokaNobel26@outlook.com",
            "password": "492nCG629EG",
            "source": "api",
            "ads_browser_id": "k12a6fch",
            "ads_browser_num": "num_014",
            "proxy_ip": "192.168.1.14",
            "proxy_country": "JP",
            "is_valid": False,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": "2025-07-26 22:00:00",
            "remark": "account"
        },
        {
            "address": "SaladoClora925@outlook.com",
            "password": "79l74j5G",
            "source": "import",
            "ads_browser_id": "k12a6fcf",
            "ads_browser_num": "num_015",
            "proxy_ip": "192.168.1.15",
            "proxy_country": "DE",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-25 23:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "HolsombackAtoe5085@outlook.com",
            "password": "u25W3i86m",
            "source": "manual",
            "ads_browser_id": "k12a6fcd",
            "ads_browser_num": "num_016",
            "proxy_ip": "192.168.1.16",
            "proxy_country": "US",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "HershaDaigneault877@outlook.com",
            "password": "VTvA12X99w",
            "source": "api",
            "ads_browser_id": "k12a6fci",
            "ads_browser_num": "num_017",
            "proxy_ip": "192.168.1.17",
            "proxy_country": "UK",
            "is_valid": False,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-26 00:00:00",
            "stop_time": "2025-07-26 23:00:00",
            "remark": "account"
        },
        {
            "address": "BojeBlakesley7954@outlook.com",
            "password": "s08B1Y7Ae",
            "source": "import",
            "ads_browser_id": "k12a6i3n",
            "ads_browser_num": "num_018",
            "proxy_ip": "192.168.1.18",
            "proxy_country": "CN",
            "is_valid": True,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "MamulaShelvy56@outlook.com",
            "password": "5I6o5855Z0Rj",
            "source": "manual",
            "ads_browser_id": "k12a6i3o",
            "ads_browser_num": "num_019",
            "proxy_ip": "192.168.1.19",
            "proxy_country": "JP",
            "is_valid": True,
            "is_login": True,
            "is_need_check": 1,
            "need_check_time": "2025-07-26 01:00:00",
            "stop_time": None,
            "remark": "account"
        },
        {
            "address": "WillaChavers492@outlook.com",
            "password": "51T8eI27Y",
            "source": "api",
            "ads_browser_id": "k12a6i3p",
            "ads_browser_num": "num_020",
            "proxy_ip": "192.168.1.20",
            "proxy_country": "DE",
            "is_valid": False,
            "is_login": False,
            "is_need_check": 0,
            "need_check_time": None,
            "stop_time": "2025-07-26 01:00:00",
            "remark": "account"
        }
    ]

# 示例用法
if __name__ == "__main__":
    # 初始化数据库管理器
    db_manager = PostgresDBManager()

    # 创建表
    # db_manager.create_email_content_table()
    # db_manager.create_email_list_table()

    # 查询表数据
    # db_manager.query_table("outlook_email_content")
    # db_manager.query_table("outlook_email_list")

    # 修改表结构（示例：添加新列）
    # db_manager.alter_email_content_table("status", "VARCHAR(50)")
    # db_manager.alter_email_list_table("last_login", "TIMESTAMP")

    # 插入数据
    # db_manager.insert_email_list()

    # 插入 20 条测试数据到 outlook_email_list
    test_data = get_test_data()
    db_manager.insert_email_list_batch(test_data)

    # 关闭连接
    db_manager.close_connection()
