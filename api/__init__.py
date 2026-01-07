# api/__init__.py
"""
智慧林草系统 - API层包
提供RESTful API接口
"""

from flask import Blueprint

# 创建API主蓝图 - 所有API都在/api前缀下
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 创建子蓝图
main_bp = Blueprint('main', __name__)  # 在/api下
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_bp = Blueprint('user', __name__, url_prefix='/users')
environment_bp = Blueprint('environment', __name__, url_prefix='/environment')
alert_bp = Blueprint('alert', __name__, url_prefix='/alerts')
resource_bp = Blueprint('resource', __name__, url_prefix='/resources')
device_bp = Blueprint('device', __name__, url_prefix='/devices')
statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')

def init_api(app):
    """初始化API应用"""
    # 导入路由模块（确保路由已注册到蓝图）
    from . import main, auth, user, environment, alert, resource, device, statistics
    
    # 将子蓝图注册到API主蓝图
    api_bp.register_blueprint(main_bp)
    api_bp.register_blueprint(auth_bp)
    api_bp.register_blueprint(user_bp)
    api_bp.register_blueprint(environment_bp)  # 包含区域管理
    api_bp.register_blueprint(alert_bp)
    api_bp.register_blueprint(resource_bp)
    api_bp.register_blueprint(device_bp)
    api_bp.register_blueprint(statistics_bp)
    
    # 注册API主蓝图到应用
    app.register_blueprint(api_bp)
    
    return app

__all__ = [
    'api_bp',
    'main_bp',
    'auth_bp',
    'user_bp',
    'environment_bp',  # 替换area_bp
    'alert_bp',
    'resource_bp',
    'device_bp',
    'statistics_bp',
    'init_api'
]