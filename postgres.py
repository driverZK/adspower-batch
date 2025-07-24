import psycopg2
from psycopg2 import Error

try:
    # 建立数据库连接
    connection = psycopg2.connect(
        user="mint",           # 数据库用户名
        password="",       # 数据库密码
        host="127.0.0.1",              # 数据库主机地址
        port="5432",                   # 数据库端口
        database="mint"        # 数据库名称
    )

    # 创建一个 cursor 对象来执行 PostgreSQL 命令
    cursor = connection.cursor()

    # 创建 outlook_email_content 表
    create_content_table_query = '''
        CREATE TABLE IF NOT EXISTS outlook_email_content (
            id SERIAL PRIMARY KEY,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            email_address VARCHAR(255) NOT NULL,
            email_title VARCHAR(255),
            email_content TEXT
        );
    '''
    cursor.execute(create_content_table_query)
    print("表 outlook_email_content 创建成功")

    # 创建 outlook_email_list 表
    create_list_table_query = '''
        CREATE TABLE IF NOT EXISTS outlook_email_list (
            id SERIAL PRIMARY KEY,
            create_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            address VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        );
    '''
    cursor.execute(create_list_table_query)
    connection.commit()
    print("表 outlook_email_list 创建成功")

except (Exception, Error) as error:
    print("创建表时出错:", error)

finally:
    # 关闭数据库连接
    if connection:
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
