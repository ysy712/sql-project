import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 安全密钥
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://root:password@localhost:3306/forest_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 会话配置
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    SESSION_COOKIE_HTTPONLY = True

    # 文件上传
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'

    # 角色权限
    ROLES = {
        'admin': ['all'],
        'data_admin': ['read', 'write', 'manage_data'],
        'ranger': ['read', 'report', 'manage_region'],
        'public': ['read_public'],
        'supervisor': ['read', 'audit']
    }