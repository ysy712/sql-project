# services/user_service.py
"""
用户服务层
处理用户相关的业务逻辑
"""

from models.user_model import UserModel
from utils.response_utils import ApiResponse, ResponseCode
from datetime import datetime
import logging

def _success_response(data=None, message="操作成功", total=None):
    """成功响应辅助函数"""
    return ApiResponse(
        code=ResponseCode.SUCCESS.value,
        message=message,
        data=data,
        total=total
    ).to_dict()

def _error_response(code, message="操作失败", data=None):
    """错误响应辅助函数"""
    code_value = code.value if isinstance(code, ResponseCode) else code
    return ApiResponse(
        code=code_value,
        message=message,
        data=data
    ).to_dict()

logger = logging.getLogger(__name__)

class UserService:
    """用户服务类"""
    
    @staticmethod
    def register_user(data):
        """注册用户"""
        try:
            # 验证必填字段
            required_fields = ['Username', 'Password', 'Email', 'RoleType']
            for field in required_fields:
                if field not in data or not data[field]:
                    return _error_response(
                        ResponseCode.BAD_REQUEST,
                        f'缺少必要字段: {field}'
                    )
            
            # 验证用户数据
            errors = UserModel.validate_user_data(data)
            if errors:
                return _error_response(
                    ResponseCode.BAD_REQUEST,
                    '数据验证失败',
                    data=errors
                )
            
            # 检查用户名是否已存在
            existing_user = UserModel.query.filter_by(Username=data['Username']).first()
            if existing_user:
                return _error_response(
                    ResponseCode.BAD_REQUEST,
                    '用户名已存在'
                )
            
            # 检查邮箱是否已存在
            if data.get('Email'):
                existing_email = UserModel.query.filter_by(Email=data['Email']).first()
                if existing_email:
                    return _error_response(
                        ResponseCode.BAD_REQUEST,
                        '邮箱已被注册'
                    )
            
            # 生成用户ID
            data['UserID'] = UserModel.generate_user_id(data['RoleType'])
            
            # 创建用户
            user = UserModel.create(data)
            
            return _success_response(
                message='用户创建成功',
                data=user.to_dict()
            )
            
        except ValueError as e:
            return _error_response(
                ResponseCode.BAD_REQUEST,
                str(e)
            )
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'创建用户失败: {str(e)}'
            )
    
    @staticmethod
    def update_user(user_id, data, current_user_id):
        """更新用户信息"""
        try:
            # 检查用户是否存在
            user = UserModel.find_by_id(user_id)
            if not user:
                return _error_response(
                    ResponseCode.NOT_FOUND,
                    '用户不存在'
                )
            
            # 非管理员只能修改自己的信息
            if user_id != current_user_id:
                current_user = UserModel.find_by_id(current_user_id)
                if current_user and current_user.RoleType != UserModel.ROLE_SYSTEM_ADMIN:
                    return _error_response(
                        ResponseCode.FORBIDDEN,
                        '无权修改其他用户信息'
                    )
            
            # 不能修改用户名
            if 'Username' in data:
                return _error_response(
                    ResponseCode.BAD_REQUEST,
                    '用户名不可修改'
                )
            
            # 如果修改邮箱，检查是否重复
            if 'Email' in data and data['Email']:
                existing_email = UserModel.query.filter(
                    UserModel.Email == data['Email'],
                    UserModel.UserID != user_id
                ).first()
                if existing_email:
                    return _error_response(
                        ResponseCode.BAD_REQUEST,
                        '邮箱已被其他用户使用'
                    )
            
            # 验证更新数据
            update_data = {k: v for k, v in data.items() if hasattr(user, k)}
            errors = UserModel.validate_user_data(update_data)
            if errors:
                return _error_response(
                    ResponseCode.BAD_REQUEST,
                    '数据验证失败',
                    data=errors
                )
            
            # 更新用户信息
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            from models import db
            db.session.commit()
            
            return _success_response(
                message='用户信息更新成功',
                data=user.to_dict()
            )
            
        except ValueError as e:
            return _error_response(
                ResponseCode.BAD_REQUEST,
                str(e)
            )
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'更新用户失败: {str(e)}'
            )
    
    @staticmethod
    def delete_user(user_id, current_user_id):
        """删除用户（软删除）"""
        try:
            # 检查用户是否存在
            user = UserModel.find_by_id(user_id)
            if not user:
                return _error_response(
                    ResponseCode.NOT_FOUND,
                    '用户不存在'
                )
            
            # 不能删除自己
            if user_id == current_user_id:
                return _error_response(
                    ResponseCode.FORBIDDEN,
                    '不能删除自己的账户'
                )
            
            # 软删除（标记为未激活）
            user.IsActive = False
            from models import db
            db.session.commit()
            
            return _success_response(
                message='用户删除成功'
            )
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'删除用户失败: {str(e)}'
            )
    
    @staticmethod
    def get_user_detail(user_id):
        """获取用户详情"""
        try:
            user = UserModel.find_by_id(user_id)
            if not user:
                return _error_response(
                    ResponseCode.NOT_FOUND,
                    '用户不存在'
                )
            
            user_dict = user.to_dict()
            
            # 如果有区域ID，查询区域名称
            if user.AreaID:
                from models.sensor_model import Area
                area = Area.query.get(user.AreaID)
                if area:
                    user_dict['AreaName'] = area.AreaName
            
            return _success_response(
                data=user_dict
            )
            
        except Exception as e:
            logger.error(f"获取用户详情失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'获取用户详情失败: {str(e)}'
            )
    
    @staticmethod
    def get_user_list(role_type=None, page=1, page_size=20):
        """获取用户列表"""
        try:
            from models import db
            from sqlalchemy import or_
            
            query = UserModel.query
            
            # 添加过滤条件
            if role_type:
                query = query.filter_by(RoleType=role_type)
            
            # 按创建时间倒序排列
            query = query.order_by(UserModel.CreatedTime.desc())
            
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            
            # 获取所有用户数据并添加区域名称
            users = []
            for user in pagination.items:
                user_dict = user.to_dict()
                # 如果有区域ID，查询区域名称
                if user.AreaID:
                    from models.sensor_model import Area
                    area = Area.query.get(user.AreaID)
                    if area:
                        user_dict['AreaName'] = area.AreaName
                users.append(user_dict)
            
            result = {
                'items': users,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
            return _success_response(
                data=result
            )
            
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'获取用户列表失败: {str(e)}'
            )
    
    @staticmethod
    def search_users(keyword, role_type=None, page=1, page_size=20):
        """搜索用户"""
        try:
            from sqlalchemy import or_
            from models.sensor_model import Area
            
            query = UserModel.query
            
            if keyword:
                query = query.filter(
                    or_(
                        UserModel.Username.like(f'%{keyword}%'),
                        UserModel.Email.like(f'%{keyword}%'),
                    )
                )
            
            if role_type:
                query = query.filter_by(RoleType=role_type)
            
            pagination = query.paginate(page=page, per_page=page_size, error_out=False)
            
            # 添加区域名称
            users = []
            for user in pagination.items:
                user_dict = user.to_dict()
                if user.AreaID:
                    area = Area.query.get(user.AreaID)
                    if area:
                        user_dict['AreaName'] = area.AreaName
                users.append(user_dict)
            
            result = {
                'items': users,  # 修改为 items
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
            return _success_response(
                data=result
            )
            
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'搜索用户失败: {str(e)}'
            )
    
    @staticmethod
    def get_field_workers(area_id=None):
        """获取护林员列表"""
        try:
            if area_id:
                workers = UserModel.get_field_workers_by_area(area_id)
            else:
                workers = UserModel.get_by_role(UserModel.ROLE_FIELD_WORKER)
                workers = workers.get('records', []) if isinstance(workers, dict) else workers
            
            return _success_response(
                data={'workers': workers}
            )
            
        except Exception as e:
            logger.error(f"获取护林员列表失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'获取护林员列表失败: {str(e)}'
            )
    
    @staticmethod
    def update_password(user_id, old_password, new_password, current_user_id):
        """修改密码"""
        try:
            # 检查用户是否存在
            user = UserModel.find_by_id(user_id)
            if not user:
                return _error_response(
                    ResponseCode.NOT_FOUND,
                    '用户不存在'
                )
            
            # 只能修改自己的密码，除非是管理员
            if user_id != current_user_id:
                current_user = UserModel.find_by_id(current_user_id)
                if current_user and current_user.RoleType != UserModel.ROLE_SYSTEM_ADMIN:
                    return _error_response(
                        ResponseCode.FORBIDDEN,
                        '无权修改其他用户密码'
                    )
            
            # 非管理员需要验证旧密码
            if user_id == current_user_id:
                if not user.check_password(old_password):
                    return _error_response(
                        ResponseCode.BAD_REQUEST,
                        '旧密码不正确'
                    )
            
            # 验证新密码长度
            if len(new_password) < 6:
                return _error_response(
                    ResponseCode.BAD_REQUEST,
                    '密码长度至少6个字符'
                )
            
            # 更新密码
            success = UserModel.update_password(user_id, new_password)
            if not success:
                return _error_response(
                    ResponseCode.INTERNAL_ERROR,
                    '更新密码失败'
                )
            
            return _success_response(
                message='密码修改成功'
            )
            
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            return _error_response(
                ResponseCode.INTERNAL_ERROR,
                f'修改密码失败: {str(e)}'
            )
    
    @staticmethod
    def get_users_by_role(role_type):
        """根据角色获取用户列表（兼容方法）"""
        try:
            users = UserModel.query.filter_by(RoleType=role_type, IsActive=True).all()
            return [user.to_dict() for user in users]
        except Exception as e:
            logger.error(f"获取角色用户失败: {e}")
            return []