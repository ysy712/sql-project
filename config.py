import os
from typing import Dict, Any

class Config:
    """全局配置类"""
    
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '20050801')
    DB_NAME = os.getenv('DB_NAME', 'smart_forest_grass')
    DB_CHARSET = 'utf8mb4'
    
    # 数据库连接字符串
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset={DB_CHARSET}"
    
    # SQLAlchemy配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 设置为True可查看SQL语句
    
    # 应用配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'smart-forest-grass-secret-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # 分页配置
    PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def get_db_config() -> Dict[str, Any]:
        """获取数据库配置字典"""
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'charset': Config.DB_CHARSET
        }
    
    @staticmethod
    def init_app():
        """初始化应用目录"""
        # 确保上传目录存在
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # 创建其他必要的目录
        for folder in ['static', 'templates', 'logs']:
            folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)