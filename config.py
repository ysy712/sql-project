import os
from dotenv import load_dotenv
from pathlib import Path
from urllib.parse import quote_plus

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent


class Config:
    # 基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'smart-forest-grass-secret-key-development')

    # MySQL数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '123456')
    DB_NAME = os.getenv('DB_NAME', 'smart_forest_grass_db')

    # 对密码进行URL编码（处理特殊字符）
    if DB_PASSWORD:
        encoded_password = quote_plus(DB_PASSWORD)
    else:
        encoded_password = ''

    # 构建数据库URI
    if encoded_password:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    else:
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 开发时显示SQL语句

    # API配置
    API_PREFIX = '/api/v1'

    # 分页配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 上传配置
    UPLOAD_FOLDER = BASE_DIR / 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    @staticmethod
    def init_app(app):
        # 确保上传目录存在
        Config.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        print(f"数据库连接URI: {Config.SQLALCHEMY_DATABASE_URI}")
        print(f"原始密码: {Config.DB_PASSWORD}")
        print(f"编码后密码: {Config.encoded_password}")


config = Config()