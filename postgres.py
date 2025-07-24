import psycopg2
from psycopg2 import Error
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
        """创建 outlook_email_list 表"""
        try:
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS outlook_email_list (
                    id SERIAL PRIMARY KEY,
                    create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    address VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL
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

    def insert_email_list(self, address, password):
        """向 outlook_email_list 表插入数据"""
        try:
            insert_query = '''
                INSERT INTO outlook_email_list (address, password)
                VALUES (%s, %s);
            '''
            self.cursor.execute(insert_query, (address, password))
            self.connection.commit()
            print("outlook_email_list 表插入数据成功")
        except (Exception, Error) as error:
            print("插入 outlook_email_list 数据时出错:", error)

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

# 示例用法
if __name__ == "__main__":
    # 初始化数据库管理器
    db_manager = PostgresDBManager()

    # 创建表
    # db_manager.create_email_content_table()
    # db_manager.create_email_list_table()

    # 查询表数据
    db_manager.query_table("outlook_email_content")
    db_manager.query_table("outlook_email_list")

    # 修改表结构（示例：添加新列）
    # db_manager.alter_email_content_table("status", "VARCHAR(50)")
    # db_manager.alter_email_list_table("last_login", "TIMESTAMP")

    # 关闭连接
    db_manager.close_connection()