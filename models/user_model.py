# models/user_model.py
"""
用户模型模块
包含用户信息相关的数据模型
"""

from datetime import datetime
from models import db
from .base_model import BaseModel
import bcrypt
import re


class UserModel(BaseModel):
    """用户信息模型（ORM版本）"""
    __tablename__ = 'User'
    
    # 角色类型常量（与数据库约束保持一致）
    ROLE_SYSTEM_ADMIN = '系统管理员'
    ROLE_DATA_ADMIN = '数据管理员'
    ROLE_FIELD_WORKER = '区域护林员'  
    ROLE_PUBLIC_USER = '公众用户'
    ROLE_SUPERVISOR = '监管人员'
    
    # 性别常量
    GENDER_MALE = '男'
    GENDER_FEMALE = '女'
    GENDER_UNKNOWN = '未知'
    
    # 数据库字段（与建表语句完全一致）
    UserID = db.Column(db.String(15), primary_key=True, comment='用户编号')
    Username = db.Column(db.String(30), nullable=False, unique=True, comment='用户名')
    Password = db.Column(db.String(255), nullable=False, comment='密码')
    Gender = db.Column(db.String(2), default='未知', comment='性别')  # VARCHAR(2)
    Email = db.Column(db.String(50), unique=True, comment='邮箱')  # 注意：数据库中有UNIQUE约束
    RoleType = db.Column(db.String(20), nullable=False, comment='角色类型')
    CreatedTime = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    UpdatedTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    IsActive = db.Column(db.Boolean, default=True, comment='是否激活')
    AreaID = db.Column(db.String(15), db.ForeignKey('Area.AreaID', ondelete='SET NULL', onupdate='CASCADE'), 
                   comment='负责区域ID')
    
    area = db.relationship('Area', backref='managed_users', lazy=True)
    
    def __repr__(self):
        return f'<User {self.Username} ({self.RoleType})>'
    
    # 兼容性方法
    @classmethod
    def create(cls, data: dict):
        """创建用户（加密密码）"""
        if 'Password' in data and data['Password']:
            data['Password'] = cls.hash_password(data['Password'])
        
        instance = cls(**data)
        db.session.add(instance)
        db.session.commit()
        return instance
    
    @classmethod
    def verify_password(cls, username: str, password: str):
        """验证用户名和密码"""
        user = cls.query.filter_by(Username=username).first()
        if user and user.check_password(password):
            return user
        return None
    
    @classmethod
    def create_user(cls, data: dict):
        """创建用户（兼容方法）"""
        return cls.create(data)
    
    @classmethod
    def get_user_by_id(cls, user_id: str):
        """根据ID获取用户（兼容方法）"""
        return cls.find_by_id(user_id)
    
    @classmethod
    def update_user(cls, user_id: str, data: dict):
        """更新用户（兼容方法）"""
        user = cls.find_by_id(user_id)
        if user:
            for key, value in data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            from models import db
            db.session.commit()
            return user
        return None
    
    @classmethod
    def delete_user(cls, user_id: str):
        """删除用户（软删除，兼容方法）"""
        user = cls.find_by_id(user_id)
        if user:
            user.IsActive = False
            from models import db
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_all_users(cls, page=1, page_size=20, role_type=None):
        """获取所有用户（兼容方法）"""
        query = cls.query.filter_by(IsActive=True)
        
        if role_type:
            query = query.filter_by(RoleType=role_type)
        
        query = query.order_by(cls.CreatedTime.desc())
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @classmethod
    def get_users_by_role(cls, role_type: str):
        """根据角色获取用户（兼容方法）"""
        users = cls.query.filter_by(RoleType=role_type, IsActive=True).all()
        return [user.to_dict() for user in users]

    @classmethod
    def find_by_id(cls, user_id: str):
        """根据ID查找用户"""
        return cls.query.get(user_id)
    
    @classmethod
    def find_one(cls, where=None, params=None):
        """查找一条记录（兼容旧接口）"""
        query = cls.query
        if where and params:
            if '=' in where:
                condition = where.split('=')
                if len(condition) == 2:
                    field = condition[0].strip()
                    query = query.filter(getattr(cls, field) == params[0])
        return query.first()
    
    @classmethod
    def get_paginated(cls, page=1, page_size=20, where=None, params=None, order_by=None):
        """分页查询（兼容旧接口）"""
        query = cls.query
        
        # 应用过滤条件
        if where and params:
            if 'AND' in where:
                conditions = where.split('AND')
                for condition in conditions:
                    condition = condition.strip()
                    if '=' in condition:
                        parts = condition.split('=')
                        if len(parts) == 2:
                            field = parts[0].strip()
                            query = query.filter(getattr(cls, field) == params[0])
        
        # 排序
        if order_by:
            order_field = order_by.split()[0]
            if 'DESC' in order_by.upper():
                query = query.order_by(db.desc(getattr(cls, order_field)))
            else:
                query = query.order_by(getattr(cls, order_field))
        
        # 分页
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            'records': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @classmethod
    def get_field_workers_by_area(cls, area_id: str):
        """获取指定区域的护林员（兼容旧接口）"""
        from .sensor_model import Area
        area = Area.query.get(area_id)
        if area and area.ManagerID:
            user = cls.query.get(area.ManagerID)
            if user and user.RoleType == cls.ROLE_FIELD_WORKER:
                return [user.to_dict()]
        return []
    
    @classmethod
    def search_users(cls, keyword: str, role_type: str = None, 
                     page: int = 1, page_size: int = 20):
        """搜索用户（兼容旧接口）"""
        from sqlalchemy import or_
        
        query = cls.query
        
        if keyword:
            query = query.filter(
                or_(
                    cls.Username.like(f'%{keyword}%'),
                    cls.Email.like(f'%{keyword}%'),
                )
            )
        
        if role_type:
            query = query.filter_by(RoleType=role_type)
        
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            'records': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @classmethod
    def update_password(cls, user_id: str, new_password: str) -> bool:
        """更新用户密码（兼容旧接口）"""
        user = cls.query.get(user_id)
        if user:
            user.Password = cls.hash_password(new_password)
            db.session.commit()
            return True
        return False
    
    def check_password(self, password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.Password.encode('utf-8'))
        except Exception:
            return False
    
    @classmethod
    def hash_password(cls, password: str) -> str:
        """哈希密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def _check_password(password: str, hashed_password: str) -> bool:
        """验证密码（兼容旧接口）"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    @classmethod
    def get_by_role(cls, role_type: str, page: int = 1, page_size: int = 20):
        """根据角色类型获取用户列表（兼容旧接口）"""
        query = cls.query.filter_by(RoleType=role_type)
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        return {
            'records': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @classmethod
    def validate_user_data(cls, data: dict) -> dict:
        """验证用户数据"""
        errors = {}
        
        # 验证用户名
        if 'Username' in data:
            username = data['Username']
            if len(username) < 3 or len(username) > 30:
                errors['Username'] = '用户名长度必须在3-30个字符之间'
            elif not re.match(r'^[a-zA-Z0-9_]+$', username):
                errors['Username'] = '用户名只能包含字母、数字和下划线'
        
        # 验证邮箱
        if 'Email' in data and data['Email']:
            email = data['Email']
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors['Email'] = '邮箱格式不正确'
        
        # 验证角色
        if 'RoleType' in data:
            valid_roles = [
                cls.ROLE_SYSTEM_ADMIN, 
                cls.ROLE_DATA_ADMIN, 
                cls.ROLE_FIELD_WORKER,  
                cls.ROLE_PUBLIC_USER, 
                cls.ROLE_SUPERVISOR
            ]
            if data['RoleType'] not in valid_roles:
                errors['RoleType'] = f'角色类型必须为: {", ".join(valid_roles)}'
        
        # 验证性别
        if 'Gender' in data and data['Gender']:
            valid_genders = [cls.GENDER_MALE, cls.GENDER_FEMALE, cls.GENDER_UNKNOWN]
            if data['Gender'] not in valid_genders:
                errors['Gender'] = f'性别必须为: {", ".join(valid_genders)}'
        
        return errors
    
    @classmethod
    def generate_user_id(cls, role_type: str) -> str:
        """生成用户ID"""
        # 角色代码映射
        role_codes = {
            cls.ROLE_SYSTEM_ADMIN: 'SYS',
            cls.ROLE_DATA_ADMIN: 'DATA',
            cls.ROLE_FIELD_WORKER: 'FLD',
            cls.ROLE_PUBLIC_USER: 'PUB',
            cls.ROLE_SUPERVISOR: 'SUP'
        }
        
        role_code = role_codes.get(role_type, 'USR')
        
        # 查找当前最大序号
        from sqlalchemy import func
        max_sequence = cls.query.filter(
            cls.UserID.like(f'USR-{role_code}-%')
        ).count()
        
        sequence = max_sequence + 1
        return f"USR-{role_code}-{sequence:03d}"
    
    def to_dict(self, exclude=None):
        """转换为字典（排除密码）"""
        if exclude is None:
            exclude = ['Password']
        elif 'Password' not in exclude:
            exclude.append('Password')
        return super().to_dict(exclude)