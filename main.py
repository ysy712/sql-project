#!/usr/bin/env python3
"""
智慧林草系统 - 主程序入口
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import Config
from utils.db_utils import DBUtils

def init_database():
    """初始化数据库"""
    print("正在初始化数据库...")
    
    try:
        # 检查数据库连接
        connection = DBUtils.get_connection()
        print(f"✓ 数据库连接成功: {Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}")
        
        # 检查一些系统表
        tables_to_check = ['Area', 'User']  # 根据你的实际表名调整
        
        for table in tables_to_check:
            if DBUtils.table_exists(table):
                print(f"✓ 表 {table} 已存在")
            else:
                print(f"⚠ 表 {table} 不存在")
        
        connection.close()
        
        # 显示数据库统计信息
        show_database_stats()
        
    except Exception as e:
        print(f"✗ 数据库初始化失败: {e}")
        return False
    
    return True

def show_database_stats():
    """显示数据库统计信息"""
    try:
        # 获取所有表
        query = """
            SELECT 
                TABLE_NAME,
                TABLE_ROWS as row_count,
                DATA_LENGTH as data_size,
                INDEX_LENGTH as index_size,
                CREATE_TIME
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
        """
        
        tables = DBUtils.execute_query(query, (Config.DB_NAME,))
        
        print("\n📊 数据库统计信息:")
        print("-" * 80)
        print(f"{'表名':<25} {'记录数':<10} {'数据大小':<12} {'索引大小':<12} {'创建时间'}")
        print("-" * 80)
        
        total_rows = 0
        total_data = 0
        total_index = 0
        
        for table in tables:
            row_count = table['row_count'] or 0
            data_size = table['data_size'] or 0
            index_size = table['index_size'] or 0
            
            # 格式化文件大小
            def format_size(size):
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024:
                        return f"{size:.1f} {unit}"
                    size /= 1024
                return f"{size:.1f} TB"
            
            print(f"{table['TABLE_NAME']:<25} {row_count:<10} {format_size(data_size):<12} {format_size(index_size):<12} {table['CREATE_TIME']}")
            
            total_rows += row_count
            total_data += data_size
            total_index += index_size
        
        print("-" * 80)
        print(f"{'总计':<25} {total_rows:<10} {format_size(total_data):<12} {format_size(total_index):<12}")
        
    except Exception as e:
        print(f"获取统计信息失败: {e}")

def run_tests():
    """运行测试"""
    print("\n🧪 正在运行测试...")
    
    import subprocess
    import sys
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print("测试失败:")
            print(result.stderr)
            return False
        
        print("✓ 所有测试通过!")
        return True
        
    except Exception as e:
        print(f"运行测试失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("智慧林草系统 - 调试控制台")
    print("=" * 60)
    
    # 初始化应用
    Config.init_app()
    
    while True:
        print("\n请选择操作:")
        print("1. 初始化数据库")
        print("2. 运行测试")
        print("3. 显示数据库统计")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ").strip()
        
        if choice == '1':
            init_database()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            show_database_stats()
        elif choice == '4':
            print("👋 再见!")
            break
        else:
            print("❌ 无效选项，请重新输入")

if __name__ == "__main__":
    main()