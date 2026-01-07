# api/user.py
"""
用户管理API模块
处理用户相关的CRUD操作
"""

from flask import request, g
from .decorators import jwt_required, role_required, validate_json, pagination_params, handle_exceptions
from services.user_service import UserService
from utils.response_utils import ApiResponse, ResponseCode
from . import user_bp

# 创建服务实例
user_service = UserService()

@user_bp.route('', methods=['POST'])
@validate_json()
@role_required('系统管理员')
@handle_exceptions
def create_user():
    """创建用户"""
    data = g.request_data
    
    # 调用用户服务
    result = user_service.register_user(data)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/<string:user_id>', methods=['PUT'])
@validate_json()
@jwt_required
@handle_exceptions
def update_user(user_id):
    """更新用户信息"""
    data = g.request_data
    current_user_id = g.current_user_id
    
    # 调用用户服务
    result = user_service.update_user(user_id, data, current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/<string:user_id>', methods=['DELETE'])
@role_required('系统管理员')
@handle_exceptions
def delete_user(user_id):
    """删除用户"""
    current_user_id = g.current_user_id
    
    # 调用用户服务
    result = user_service.delete_user(user_id, current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('', methods=['GET'])
@jwt_required
@pagination_params()
@handle_exceptions
def get_user_list():
    """获取用户列表"""
    page = g.page
    page_size = g.page_size
    
    # 获取查询参数
    role_type = request.args.get('role_type')
    
    # 调用用户服务
    result = user_service.get_user_list(role_type, page, page_size)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/search', methods=['GET'])
@jwt_required
@pagination_params()
@handle_exceptions
def search_users():
    """搜索用户"""
    page = g.page
    page_size = g.page_size
    
    # 获取查询参数
    keyword = request.args.get('keyword', '')
    role_type = request.args.get('role_type')
    
    # 调用用户服务
    result = user_service.search_users(keyword, role_type, page, page_size)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/<string:user_id>', methods=['GET'])
@jwt_required
@handle_exceptions
def get_user_detail(user_id):
    """获取用户详情"""
    # 调用用户服务
    result = user_service.get_user_detail(user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/field-workers', methods=['GET'])
@jwt_required
@handle_exceptions
def get_field_workers():
    """获取护林员列表"""
    # 获取查询参数
    area_id = request.args.get('area_id')
    
    # 调用用户服务
    result = user_service.get_field_workers(area_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/me', methods=['GET'])
@jwt_required
@handle_exceptions
def get_current_user():
    """获取当前用户信息"""
    current_user_id = g.current_user_id
    
    # 调用用户服务
    result = user_service.get_user_detail(current_user_id)
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)

@user_bp.route('/<string:user_id>/password', methods=['PUT'])
@validate_json()
@jwt_required
@handle_exceptions
def change_password(user_id):
    """修改密码"""
    data = g.request_data
    current_user_id = g.current_user_id
    
    # 验证必填字段
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not new_password:
        return ApiResponse.error(
            ResponseCode.PARAMS_ERROR,
            '新密码不能为空'
        ), ResponseCode.PARAMS_ERROR.value
    
    # 调用用户服务
    result = user_service.update_password(
        user_id, old_password, new_password, current_user_id
    )
    
    return result, result.get('code', ResponseCode.INTERNAL_ERROR.value)