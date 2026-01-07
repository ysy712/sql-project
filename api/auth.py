# api/auth.py
"""
认证API模块
处理用户登录、登出、权限验证等接口
"""

from flask import request, g
from .decorators import validate_json, handle_exceptions, jwt_required, role_required
from services.auth_service import AuthService
import logging

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

from . import auth_bp


@auth_bp.route('/login', methods=['POST'])
@validate_json()
@handle_exceptions
def login():
    """用户登录"""
    data = g.request_data
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        response = ApiResponse(
            code=ResponseCode.BAD_REQUEST.value,
            message="用户名和密码不能为空"
        )
        return response.to_dict(), ResponseCode.BAD_REQUEST.value
    
    # 获取客户端信息
    ip_address = request.remote_addr
    user_agent = request.user_agent.string if request.user_agent else None
    
    # 调用认证服务
    result = AuthService.login(username, password, ip_address, user_agent)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/logout', methods=['POST'])
@handle_exceptions
def logout():
    """用户登出"""
    # 获取JWT令牌
    auth_header = request.headers.get('Authorization')
    token = auth_header if auth_header else ''
    
    # 获取用户ID（如果有的话）
    user_id = None
    try:
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
    except:
        pass
    
    # 调用认证服务
    result = AuthService.logout(user_id, token)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/verify', methods=['GET'])
@handle_exceptions
def verify_token():
    """验证令牌"""
    # 获取JWT令牌
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        response = ApiResponse(
            code=ResponseCode.UNAUTHORIZED.value,
            message="未提供认证令牌"
        )
        return response.to_dict(), ResponseCode.UNAUTHORIZED.value
    
    # 调用认证服务
    result = AuthService.verify_token(auth_header)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/change-password', methods=['POST'])
@validate_json()
@handle_exceptions
@jwt_required
def change_password():
    """修改密码"""
    data = g.request_data
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        response = ApiResponse(
            code=ResponseCode.BAD_REQUEST.value,
            message="旧密码和新密码不能为空"
        )
        return response.to_dict(), ResponseCode.BAD_REQUEST.value
    
    current_user_id = g.current_user_id
    
    # 调用认证服务
    result = AuthService.change_password(current_user_id, old_password, new_password)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/reset-password', methods=['POST'])
@validate_json()
@handle_exceptions
@role_required('系统管理员')
def reset_password():
    """重置密码（管理员操作）"""
    data = g.request_data
    
    username = data.get('username')
    email = data.get('email')
    new_password = data.get('new_password')
    
    if not username or not new_password:
        response = ApiResponse(
            code=ResponseCode.BAD_REQUEST.value,
            message="用户名和新密码不能为空"
        )
        return response.to_dict(), ResponseCode.BAD_REQUEST.value
    
    current_user_id = g.current_user_id
    
    # 调用认证服务
    result = AuthService.reset_password(username, email, new_password, current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/permission-check', methods=['GET'])
@handle_exceptions
@jwt_required
def check_permission():
    """检查权限"""
    # 获取查询参数
    required_role = request.args.get('role')
    required_permission = request.args.get('permission')
    
    current_user_id = g.current_user_id
    
    # 调用认证服务
    result = AuthService.check_permission(current_user_id, required_role, required_permission)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/refresh', methods=['POST'])
@handle_exceptions
@jwt_required
def refresh_token():
    """刷新令牌"""
    # 获取JWT令牌
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        response = ApiResponse(
            code=ResponseCode.UNAUTHORIZED.value,
            message="未提供认证令牌"
        )
        return response.to_dict(), ResponseCode.UNAUTHORIZED.value
    
    token = auth_header.replace('Bearer ', '')
    
    # 验证并刷新令牌
    result = AuthService.verify_token(auth_header)
    
    if result['code'] == ResponseCode.SUCCESS.value:
        user_id = result['data']['user']['UserID']
        role_type = result['data']['user']['RoleType']
        
        from services.auth_service import AuthService as AS
        new_token = AS._generate_jwt_token(user_id, role_type)
        
        response = ApiResponse(
            code=ResponseCode.SUCCESS.value,
            message="令牌刷新成功",
            data={
                'token': new_token,
                'expires_in': AS.JWT_EXPIRATION_HOURS * 3600
            }
        )
        return response.to_dict(), ResponseCode.SUCCESS.value
    else:
        return result, result.get('code', ResponseCode.UNAUTHORIZED.value)


@auth_bp.route('/register', methods=['POST'])
@validate_json()
@handle_exceptions
def register():
    """用户注册"""
    from services.user_service import UserService
    
    data = g.request_data
    
    # 必填字段验证
    required_fields = ['Username', 'Password', 'RoleType']
    for field in required_fields:
        if field not in data:
            response = ApiResponse(
                code=ResponseCode.BAD_REQUEST.value,
                message=f"缺少必要字段: {field}"
            )
            return response.to_dict(), ResponseCode.BAD_REQUEST.value
    
    # 调用用户服务注册
    user_service = UserService()
    result = user_service.register_user(data)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/profile', methods=['GET'])
@handle_exceptions
@jwt_required
def get_profile():
    """获取用户个人信息"""
    from services.user_service import UserService
    
    current_user_id = g.current_user_id
    
    user_service = UserService()
    result = user_service.get_user_detail(current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)


@auth_bp.route('/profile', methods=['PUT'])
@validate_json()
@handle_exceptions
@jwt_required
def update_profile():
    """更新用户个人信息"""
    data = g.request_data
    current_user_id = g.current_user_id
    
    from services.user_service import UserService
    user_service = UserService()
    
    # 移除不允许修改的字段
    if 'UserID' in data:
        del data['UserID']
    if 'Password' in data:
        del data['Password']  # 密码修改使用专门的接口
    if 'RoleType' in data:
        del data['RoleType']  # 角色不能自己修改
    
    result = user_service.update_user(current_user_id, data, current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)