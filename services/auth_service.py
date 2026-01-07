# services/auth_service.py
"""
身份认证服务
处理用户登录、权限验证等业务逻辑
"""

from typing import Dict, Any, Optional
import re
from datetime import datetime, timedelta
import jwt
from .base_service import BaseService
from models.user_model import UserModel
from utils.response_utils import ResponseCode
import logging
logger = logging.getLogger(__name__)

class AuthService(BaseService):
    """身份认证服务"""
    
    # JWT配置
    JWT_SECRET_KEY = 'smart-forest-grass-jwt-secret-key-change-in-production'
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    def __init__(self):
        super().__init__(UserModel)
    
    @classmethod
    def login(cls, username: str, password: str, 
             ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """用户登录"""
        try:
            # 验证用户名和密码
            if not username or not password:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "用户名和密码不能为空")
            
            # 验证用户是否存在
            user = UserModel.verify_password(username, password)
            if not user:
                # 记录失败的登录尝试
                cls._log_failed_login(username, ip_address, user_agent)
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "用户名或密码错误")
            
            # 生成JWT令牌
            token = cls._generate_jwt_token(user.UserID, user.RoleType)
            
            # 记录成功的登录
            cls.log_operation(user.UserID, '用户登录', 'User', 
                            f"用户 {username} 登录成功", ip_address=ip_address, 
                            user_agent=user_agent)
            
            # 获取用户信息（移除密码）
            user_data = user.to_dict()
            
            return cls.success_response(
                data={
                    'token': token,
                    'user': user_data,
                    'expires_in': cls.JWT_EXPIRATION_HOURS * 3600
                },
                message="登录成功"
            )
            
        except Exception as e:
            logger.error(f"用户登录失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "登录失败", str(e))
    
    @classmethod
    def logout(cls, user_id: str, token: str) -> Dict[str, Any]:
        """用户登出"""
        try:
            # 记录登出操作
            cls.log_operation(user_id, '用户登出', 'User', 
                            f"用户登出，令牌失效")
            
            return cls.success_response(message="登出成功")
            
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "登出失败", str(e))
    
    @classmethod
    def verify_token(cls, token: str) -> Dict[str, Any]:
        """验证JWT令牌"""
        try:
            if not token:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "未提供令牌")
            
            # 验证令牌格式
            if not token.startswith('Bearer '):
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "令牌格式不正确")
            
            token = token.replace('Bearer ', '')
            
            # 解析令牌
            try:
                payload = jwt.decode(
                    token, 
                    cls.JWT_SECRET_KEY, 
                    algorithms=[cls.JWT_ALGORITHM]
                )
            except jwt.ExpiredSignatureError:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "令牌已过期")
            except jwt.InvalidTokenError:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "无效的令牌")
            
            # 检查用户是否存在
            user_id = payload.get('user_id')
            user = UserModel.find_by_id(user_id)
            if not user:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "用户不存在")
            
            # 返回用户信息
            user_data = user.to_dict()
            
            return cls.success_response(
                data={
                    'user': user_data,
                    'payload': payload
                },
                message="令牌验证成功"
            )
            
        except Exception as e:
            logger.error(f"令牌验证失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "令牌验证失败", str(e))
    
    @classmethod
    def check_permission(cls, user_id: str, required_role: str = None, 
                        required_permission: str = None) -> Dict[str, Any]:
        """检查用户权限"""
        try:
            # 获取用户信息
            user = UserModel.find_by_id(user_id)
            if not user:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, 
                                        "用户不存在")
            
            # 检查角色权限
            if required_role:
                # 定义角色权限等级
                role_levels = {
                    UserModel.ROLE_SYSTEM_ADMIN: 5,  # 最高权限
                    UserModel.ROLE_SUPERVISOR: 4,
                    UserModel.ROLE_DATA_ADMIN: 3,
                    UserModel.ROLE_FIELD_WORKER: 2,
                    UserModel.ROLE_PUBLIC_USER: 1     # 最低权限
                }
                
                user_role = user.RoleType
                user_level = role_levels.get(user_role, 0)
                required_level = role_levels.get(required_role, 0)
                
                if user_level < required_level:
                    return cls.error_response(ResponseCode.FORBIDDEN.value, 
                                            f"需要 {required_role} 权限，当前为 {user_role}")
            
            # 检查具体权限（这里可以根据需要扩展）
            if required_permission:
                # 在实际项目中，这里可以检查具体的权限代码
                pass
            
            return cls.success_response(
                data={'has_permission': True, 'user_role': user.RoleType},
                message="权限检查通过"
            )
            
        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "权限检查失败", str(e))
    
    @classmethod
    def change_password(cls, user_id: str, old_password: str, 
                       new_password: str) -> Dict[str, Any]:
        """修改密码"""
        try:
            # 验证必需字段
            if not old_password or not new_password:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "旧密码和新密码不能为空")
            
            # 验证新密码强度
            if len(new_password) < 8:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "新密码长度不能少于8个字符")
            
            # 获取用户信息
            user = UserModel.find_by_id(user_id)
            if not user:
                return cls.error_response(ResponseCode.NOT_FOUND.value, "用户不存在")
            
            # 验证旧密码
            if not user.check_password(old_password):
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "旧密码错误")
            
            # 更新密码
            user.Password = UserModel.hash_password(new_password)
            from models import db
            db.session.commit()
            
            # 记录操作日志
            cls.log_operation(user_id, '修改密码', 'User', 
                            f"用户修改密码成功")
            
            return cls.success_response(message="密码修改成功")
                
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "修改密码失败", str(e))
    
    @classmethod
    def reset_password(cls, username: str, email: str, 
                      new_password: str, current_user_id: str) -> Dict[str, Any]:
        """重置密码（管理员操作）"""
        try:
            # 权限检查：只有管理员可以重置密码
            current_user = UserModel.find_by_id(current_user_id)
            if not current_user:
                return cls.error_response(ResponseCode.UNAUTHORIZED.value, "用户不存在")
            
            allowed_roles = [UserModel.ROLE_SYSTEM_ADMIN]
            if current_user.RoleType not in allowed_roles:
                return cls.error_response(ResponseCode.FORBIDDEN.value, 
                                        "只有系统管理员可以重置密码")
            
            # 验证必需字段
            if not username or not new_password:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "用户名和新密码不能为空")
            
            # 验证新密码强度
            if len(new_password) < 8:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "新密码长度不能少于8个字符")
            
            # 查找用户
            user = UserModel.query.filter_by(Username=username).first()
            if not user:
                return cls.error_response(ResponseCode.NOT_FOUND.value, "用户不存在")
            
            # 如果提供了邮箱，验证邮箱是否匹配
            if email and user.Email != email:
                return cls.error_response(ResponseCode.BAD_REQUEST.value, 
                                        "邮箱不匹配")
            
            # 重置密码
            user.Password = UserModel.hash_password(new_password)
            from models import db
            db.session.commit()
            
            # 记录操作日志
            cls.log_operation(current_user_id, '重置密码', 'User', 
                            f"重置用户 {username} 的密码")
            
            return cls.success_response(message="密码重置成功")
                
        except Exception as e:
            logger.error(f"重置密码失败: {e}")
            return cls.error_response(ResponseCode.INTERNAL_ERROR.value, 
                                    "重置密码失败", str(e))
    
    @classmethod
    def _generate_jwt_token(cls, user_id: str, role_type: str) -> str:
        """生成JWT令牌"""
        payload = {
            'user_id': user_id,
            'role': role_type,
            'exp': datetime.utcnow() + timedelta(hours=cls.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, cls.JWT_SECRET_KEY, algorithm=cls.JWT_ALGORITHM)
        return token
    
    @classmethod
    def _log_failed_login(cls, username: str, ip_address: str = None, 
                         user_agent: str = None):
        """记录失败的登录尝试"""
        try:
            from models.log_model import OperationLogModel
            OperationLogModel.log_operation(
                user_id=None,
                operation_type='用户登录',
                operation_table='User',
                operation_content=f"用户 {username} 登录失败",
                ip_address=ip_address,
                user_agent=user_agent,
                result=OperationLogModel.RESULT_FAILURE,
                error_message='用户名或密码错误'
            )
        except Exception as e:
            logger.error(f"记录失败登录日志失败: {e}")