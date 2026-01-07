# models/__init__.py
"""
智慧林草系统 - 模型包
提供所有数据库实体类的定义
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from .base_model import BaseModel
from .sensor_model import Area, Sensor, Monitor
from .user_model import UserModel
from .log_model import OperationLogModel
from .resource_model import Resource, ResourceChangeLog

__all__ = [
    'db',
    'BaseModel',
    'Area',
    'Sensor',
    'Monitor',
    'UserModel',
    'OperationLogModel',
    'Resource',
    'ResourceChangeLog',
]