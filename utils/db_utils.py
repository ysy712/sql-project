import pymysql
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager
from config import Config
import logging

# 配置日志
logger = logging.getLogger(__name__)

class DBUtils:
    """数据库工具类"""
    
    @staticmethod
    def get_connection():
        """获取数据库连接"""
        try:
            config = Config.get_db_config()
            connection = pymysql.connect(**config)
            return connection
        except pymysql.Error as e:
            logger.error(f"数据库连接失败: {e}")
            raise
    
    @staticmethod
    @contextmanager
    def get_cursor():
        """获取游标的上下文管理器"""
        connection = None
        cursor = None
        try:
            connection = DBUtils.get_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            yield cursor
            connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询语句"""
        with DBUtils.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    
    @staticmethod
    def execute_update(query: str, params: tuple = None) -> int:
        """执行更新语句，返回影响的行数"""
        with DBUtils.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.rowcount
    
    @staticmethod
    def execute_insert(query: str, params: tuple = None) -> int:
        """执行插入语句，返回最后插入的ID"""
        with DBUtils.get_cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid
    
    @staticmethod
    def execute_many(query: str, params_list: List[tuple]) -> int:
        """批量执行语句"""
        with DBUtils.get_cursor() as cursor:
            cursor.executemany(query, params_list)
            return cursor.rowcount
    
    @staticmethod
    def table_exists(table_name: str) -> bool:
        """检查表是否存在"""
        query = """
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """
        result = DBUtils.execute_query(query, (Config.DB_NAME, table_name))
        return result[0]['count'] > 0
    
    @staticmethod
    def get_table_structure(table_name: str) -> List[Dict[str, Any]]:
        """获取表结构信息"""
        query = """
            SELECT 
                column_name, 
                data_type, 
                is_nullable,
                column_default,
                column_key,
                extra,
                column_comment
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """
        return DBUtils.execute_query(query, (Config.DB_NAME, table_name))