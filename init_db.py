#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库和表结构
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import pymysql
from config import Config

def execute_sql_file(connection, file_path: Path):
    """执行SQL文件"""
    try:
        if not file_path.exists():
            print(f"警告: SQL文件不存在: {file_path}")
            return False
        
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（简单的分割方式，实际项目中可能需要更复杂的解析）
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        cursor = connection.cursor()
        
        success_count = 0
        error_count = 0
        
        for stmt in sql_statements:
            try:
                cursor.execute(stmt)
                success_count += 1
            except pymysql.Error as e:
                error_count += 1
                print(f"执行SQL语句失败 ({error_count}): {e}")
                print(f"问题语句: {stmt[:100]}...")
        
        connection.commit()
        cursor.close()
        
        print(f"✓ 执行完成: 成功 {success_count}, 失败 {error_count}")
        return error_count == 0
        
    except Exception as e:
        print(f"执行SQL文件失败: {e}")
        return False

def main():
    """主函数"""
    print("智慧林草系统 - 数据库初始化")
    print("=" * 50)
    
    try:
        # 获取基础配置（不包含数据库名）
        base_config = Config.get_db_config()
        
        # 第一步：连接到MySQL服务器
        print("1. 连接到MySQL服务器...")
        connection = pymysql.connect(
            host=base_config['host'],
            port=base_config['port'],
            user=base_config['user'],
            password=base_config['password'],
            charset=base_config['charset']
        )
        
        cursor = connection.cursor()
        
        # 第二步：检查数据库是否存在
        print(f"2. 检查数据库 {Config.DB_NAME}...")
        cursor.execute(f"SHOW DATABASES LIKE '{Config.DB_NAME}'")
        database_exists = cursor.fetchone() is not None
        
        if database_exists:
            choice = input(f"数据库 {Config.DB_NAME} 已存在，是否删除并重建？ (y/N): ").strip().lower()
            if choice == 'y':
                print(f"删除数据库 {Config.DB_NAME}...")
                cursor.execute(f"DROP DATABASE {Config.DB_NAME}")
                connection.commit()
                database_exists = False
            else:
                print("使用现有数据库...")
                connection.close()
                return
        
        # 第三步：创建数据库
        if not database_exists:
            print(f"3. 创建数据库 {Config.DB_NAME}...")
            cursor.execute(f"""
                CREATE DATABASE {Config.DB_NAME} 
                CHARACTER SET {Config.DB_CHARSET}
                COLLATE {Config.DB_CHARSET}_unicode_ci
            """)
            connection.commit()
        
        cursor.close()
        connection.close()
        
        # 第四步：连接到新创建的数据库
        print(f"4. 连接到数据库 {Config.DB_NAME}...")
        connection = pymysql.connect(**Config.get_db_config())
        
        # 第五步：执行DDL文件（如果有的话）
        ddl_file = Path(__file__).parent / "ddl" / "init_tables.sql"
        if ddl_file.exists():
            print("5. 执行DDL文件创建表结构...")
            execute_sql_file(connection, ddl_file)
        else:
            print("5. 未找到DDL文件，跳过表创建")
        
        connection.close()
        
        print("\n✅ 数据库初始化完成!")
        
    except pymysql.Error as e:
        print(f"❌ 数据库操作失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()