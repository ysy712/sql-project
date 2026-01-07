# api/decorators.py
"""
API装饰器
提供权限验证、参数验证等装饰器
"""

from functools import wraps
from flask import request, g
import jwt
from config import Config
import logging
from models.user_model import UserModel  # 修改导入路径

logger = logging.getLogger(__name__)

# 响应工具导入
try:
    from utils.response_utils import ApiResponse, ResponseCode
except ImportError as e:
    print(f"导入response_utils失败: {e}")
    # 本地定义
    from enum import Enum
    
    class ResponseCode(Enum):
        SUCCESS = 200
        BAD_REQUEST = 400
        UNAUTHORIZED = 401
        FORBIDDEN = 403
        NOT_FOUND = 404
        INTERNAL_ERROR = 500
    
    class ApiResponse:
        def __init__(self, code, message="", data=None, total=None):
            self.code = code
            self.message = message
            self.data = data
            self.total = total
        
        def to_dict(self):
            result = {
                "code": self.code,
                "message": self.message,
                "data": self.data
            }
            if self.total is not None:
                result["total"] = self.total
            return result


def jwt_required(f):
    """JWT认证装饰器（使用pyjwt验证）"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print(f"[JWT DEBUG] 开始JWT验证")
            auth_header = request.headers.get('Authorization')
            print(f"[JWT DEBUG] Authorization头: {auth_header}")
            
            if not auth_header:
                print(f"[JWT DEBUG] 缺少Authorization头")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="缺少认证token"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            
            # 提取token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != 'Bearer':
                print(f"[JWT DEBUG] Token格式不正确: {auth_header}")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="Token格式不正确"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            
            token = parts[1]
            print(f"[JWT DEBUG] Token: {token[:30]}...")
            
            # 使用pyjwt验证token（与auth_service.py保持一致）
            try:
                from services.auth_service import AuthService
                print(f"[JWT DEBUG] 导入AuthService成功")
                print(f"[JWT DEBUG] 使用密钥: {AuthService.JWT_SECRET_KEY[:10]}...")
                print(f"[JWT DEBUG] 使用算法: {AuthService.JWT_ALGORITHM}")
                
                payload = jwt.decode(
                    token, 
                    AuthService.JWT_SECRET_KEY, 
                    algorithms=[AuthService.JWT_ALGORITHM]
                )
                print(f"[JWT DEBUG] Token解码成功")
                print(f"[JWT DEBUG] Payload: {payload}")
                
            except jwt.ExpiredSignatureError as e:
                print(f"[JWT DEBUG] Token已过期: {e}")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="Token已过期"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            except jwt.InvalidTokenError as e:
                print(f"[JWT DEBUG] 无效的Token: {e}")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="无效的Token"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            except Exception as e:
                print(f"[JWT DEBUG] Token解码异常: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="Token验证失败"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            
            # 检查用户是否存在 - 使用ORM版本的UserModel
            user_id = payload.get('user_id')
            print(f"[JWT DEBUG] Token中的user_id: {user_id}")
            
            if not user_id:
                print(f"[JWT DEBUG] Token中缺少用户ID")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="Token中缺少用户ID"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            
            user = UserModel.find_by_id(user_id)
            if not user:
                print(f"[JWT DEBUG] 用户不存在: {user_id}")
                response = ApiResponse(
                    code=ResponseCode.UNAUTHORIZED.value,
                    message="用户不存在"
                )
                return response.to_dict(), ResponseCode.UNAUTHORIZED.value
            
            # 将用户ID保存到g对象中
            g.current_user_id = user_id
            print(f"[JWT DEBUG] JWT验证通过，用户ID: {user_id}")
            
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"JWT认证失败: {e}")
            print(f"[JWT DEBUG] 装饰器异常: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            response = ApiResponse(
                code=ResponseCode.UNAUTHORIZED.value,
                message="认证失败，请重新登录"
            )
            return response.to_dict(), ResponseCode.UNAUTHORIZED.value
    
    return decorated_function


def role_required(required_role):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                from services.auth_service import AuthService
                
                current_user_id = g.current_user_id
                
                # 检查权限
                result = AuthService.check_permission(current_user_id, required_role)
                if result['code'] != ResponseCode.SUCCESS.value:
                    return result, ResponseCode.FORBIDDEN.value
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"角色权限检查失败: {e}")
                response = ApiResponse(
                    code=ResponseCode.INTERNAL_ERROR.value,
                    message="权限检查失败"
                )
                return response.to_dict(), ResponseCode.INTERNAL_ERROR.value
        
        return decorated_function
    return decorator


def validate_json(schema=None):
    """JSON数据验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                if not request.is_json:
                    response = ApiResponse(
                        code=ResponseCode.BAD_REQUEST.value,
                        message="请求必须是JSON格式"
                    )
                    return response.to_dict(), ResponseCode.BAD_REQUEST.value
                
                data = request.get_json()
                
                # 如果有schema，进行数据验证
                if schema:
                    errors = schema.validate(data)
                    if errors:
                        response = ApiResponse(
                            code=ResponseCode.BAD_REQUEST.value,
                            message="数据验证失败",
                            data=errors
                        )
                        return response.to_dict(), ResponseCode.BAD_REQUEST.value
                
                # 将验证后的数据保存到g对象中
                g.request_data = data
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"JSON数据验证失败: {e}")
                response = ApiResponse(
                    code=ResponseCode.BAD_REQUEST.value,
                    message="数据格式错误"
                )
                return response.to_dict(), ResponseCode.BAD_REQUEST.value
        
        return decorated_function
    return decorator


def pagination_params(default_page=1, default_page_size=20):
    """分页参数装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                page = request.args.get('page', default_page, type=int)
                page_size = request.args.get('page_size', default_page_size, type=int)
                
                # 验证分页参数
                if page < 1:
                    page = default_page
                
                if page_size < 1 or page_size > 100:
                    page_size = default_page_size
                
                # 将分页参数保存到g对象中
                g.page = page
                g.page_size = page_size
                
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"分页参数处理失败: {e}")
                response = ApiResponse(
                    code=ResponseCode.BAD_REQUEST.value,
                    message="分页参数错误"
                )
                return response.to_dict(), ResponseCode.BAD_REQUEST.value
        
        return decorated_function
    return decorator


def handle_exceptions(f):
    """异常处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API处理异常: {e}", exc_info=True)
            response = ApiResponse(
                code=ResponseCode.INTERNAL_ERROR.value,
                message="服务器内部错误",
                data=str(e) if hasattr(e, '__str__') else None
            )
            return response.to_dict(), ResponseCode.INTERNAL_ERROR.value
    
    return decorated_function


def log_operation(operation_type):
    """操作日志装饰器"""
    def decorator(f):
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                # 执行原始函数
                result = f(*args, **kwargs)
                
                # 记录操作日志
                current_user_id = g.current_user_id
                operation_content = f"{operation_type}操作"
                
                from services.base_service import BaseService
                BaseService.log_operation(
                    user_id=current_user_id,
                    operation_type=operation_type,
                    operation_content=operation_content
                )
                
                return result
            except Exception as e:
                logger.error(f"记录操作日志失败: {e}")
                # 即使日志记录失败，也不影响主要业务
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator