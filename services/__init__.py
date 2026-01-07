# services/__init__.py
"""
智慧林草系统 - 服务层包
提供业务逻辑处理服务
"""

from .base_service import BaseService
from .user_service import UserService
from .sensor_service import AreaService, SensorService, MonitorService
from .auth_service import AuthService
from .resource_service import ResourceService, ResourceChangeLogService

# 为了兼容性，保留原来的名称
EnvironmentService = MonitorService

__all__ = [
    'BaseService',
    'UserService',
    'AreaService',
    'SensorService',
    'MonitorService',
    'EnvironmentService',
    'AuthService',
    'ResourceService',
    'ResourceChangeLogService',
]