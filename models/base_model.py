from datetime import datetime
from typing import Dict, Any, Optional, List
from utils.db_utils import DBUtils
import logging

logger = logging.getLogger(__name__)

class BaseModel:
    """基础模型类"""
    
    TABLE_NAME = None  # 子类必须重写
    
    @classmethod
    def create_table(cls):
        """创建表（如果不存在）"""
        if not DBUtils.table_exists(cls.TABLE_NAME):
            logger.info(f"表 {cls.TABLE_NAME} 不存在，跳过创建")
            return False
        return True
    
    @classmethod
    def count(cls, where: str = None, params: tuple = None) -> int:
        """统计记录数"""
        query = f"SELECT COUNT(*) as count FROM {cls.TABLE_NAME}"
        if where:
            query += f" WHERE {where}"
        
        result = DBUtils.execute_query(query, params)
        return result[0]['count'] if result else 0
    
    @classmethod
    def find_one(cls, where: str = None, params: tuple = None, 
                 order_by: str = None) -> Optional[Dict[str, Any]]:
        """查找单条记录"""
        query = f"SELECT * FROM {cls.TABLE_NAME}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        query += " LIMIT 1"
        
        results = DBUtils.execute_query(query, params)
        return results[0] if results else None
    
    @classmethod
    def find_by_id(cls, record_id: Any) -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        return cls.find_one("id = %s", (record_id,))
    
    @classmethod
    def find_all(cls, where: str = None, params: tuple = None,
                 order_by: str = None, limit: int = None, 
                 offset: int = None) -> List[Dict[str, Any]]:
        """查找所有记录"""
        query = f"SELECT * FROM {cls.TABLE_NAME}"
        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit is not None:
            query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
        
        return DBUtils.execute_query(query, params)
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> int:
        """创建记录"""
        if not data:
            raise ValueError("创建数据不能为空")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {cls.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        
        return DBUtils.execute_insert(query, tuple(data.values()))
    
    @classmethod
    def update(cls, record_id: Any, data: Dict[str, Any]) -> int:
        """更新记录"""
        if not data:
            raise ValueError("更新数据不能为空")
        
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {cls.TABLE_NAME} SET {set_clause} WHERE id = %s"
        
        params = tuple(data.values()) + (record_id,)
        return DBUtils.execute_update(query, params)
    
    @classmethod
    def delete(cls, record_id: Any) -> int:
        """删除记录"""
        query = f"DELETE FROM {cls.TABLE_NAME} WHERE id = %s"
        return DBUtils.execute_update(query, (record_id,))
    
    @classmethod
    def bulk_create(cls, data_list: List[Dict[str, Any]]) -> int:
        """批量创建记录"""
        if not data_list:
            return 0
        
        # 确保所有字典有相同的键
        keys = data_list[0].keys()
        for data in data_list[1:]:
            if set(data.keys()) != set(keys):
                raise ValueError("批量插入的数据必须具有相同的键")
        
        columns = ', '.join(keys)
        placeholders = ', '.join(['%s'] * len(keys))
        query = f"INSERT INTO {cls.TABLE_NAME} ({columns}) VALUES ({placeholders})"
        
        params_list = [tuple(data[key] for key in keys) for data in data_list]
        return DBUtils.execute_many(query, params_list)
    
    @classmethod
    def get_paginated(cls, page: int = 1, page_size: int = 20, 
                      where: str = None, params: tuple = None,
                      order_by: str = None) -> Dict[str, Any]:
        """分页查询"""
        offset = (page - 1) * page_size
        total = cls.count(where, params)
        
        records = cls.find_all(where, params, order_by, page_size, offset)
        
        return {
            'records': records,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }