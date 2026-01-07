# services/base_service.py
from typing import List, Dict, Any, Optional
from models import db
from utils.response_utils import ResponseCode
import logging

logger = logging.getLogger(__name__)

class BaseService:
    """基础服务类"""

    def __init__(self, model_class):
        self.model_class = model_class

    def get_by_id(self, record_id: Any) -> Optional[Any]:
        """根据ID获取记录"""
        return self.model_class.query.get(record_id)

    def get_all(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """获取所有记录（支持分页和过滤）

        Args:
            page: 页码
            per_page: 每页数量
            **filters: 过滤条件

        Returns:
            包含记录和分页信息的字典
        """
        query = self.model_class.query

        # 应用过滤条件
        for field, value in filters.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                if isinstance(value, tuple) and len(value) == 2:
                    # 范围查询，如: created_at=('>=', '2024-01-01')
                    op, val = value
                    if op == '>=':
                        query = query.filter(column >= val)
                    elif op == '<=':
                        query = query.filter(column <= val)
                    elif op == '>':
                        query = query.filter(column > val)
                    elif op == '<':
                        query = query.filter(column < val)
                    elif op == 'like':
                        query = query.filter(column.like(f'%{val}%'))
                else:
                    # 精确匹配
                    query = query.filter(column == value)

        # 执行分页查询
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'items': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    def create(self, data: Dict[str, Any]) -> Any:
        """创建新记录"""
        instance = self.model_class(**data)
        db.session.add(instance)
        db.session.commit()
        # 刷新实例，确保获取数据库端最终值（如时间被截断到秒）
        try:
            db.session.refresh(instance)
        except Exception:
            # 如果刷新失败也不阻断主流程
            db.session.rollback()
        return instance

    def update(self, record_id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """更新记录"""
        instance = self.get_by_id(record_id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
        return instance

    def delete(self, record_id: Any) -> bool:
        """删除记录"""
        instance = self.get_by_id(record_id)
        if instance:
            db.session.delete(instance)
            db.session.commit()
            return True
        return False

    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[Any]:
        """批量创建记录"""
        instances = [self.model_class(**data) for data in data_list]
        db.session.add_all(instances)
        db.session.commit()
        return instances

    def count(self, **filters) -> int:
        """统计记录数量"""
        query = self.model_class.query

        for field, value in filters.items():
            if hasattr(self.model_class, field):
                column = getattr(self.model_class, field)
                query = query.filter(column == value)

        return query.count()
    
    # 以下是新增的兼容性方法
    @staticmethod
    def success_response(data=None, message="操作成功", total=None):
        """成功响应"""
        from utils.response_utils import ApiResponse
        return ApiResponse(
            code=ResponseCode.SUCCESS.value,
            message=message,
            data=data,
            total=total
        ).to_dict()
    
    @staticmethod
    def error_response(code, message="操作失败", data=None):
        """错误响应"""
        from utils.response_utils import ApiResponse
        return ApiResponse(
            code=code,
            message=message,
            data=data
        ).to_dict()
    
    @classmethod
    def log_operation(cls, user_id, operation_type, operation_table=None, 
                     operation_content=None, **kwargs):
        """记录操作日志"""
        try:
            from models.log_model import OperationLogModel
            OperationLogModel.log_operation(
                user_id=user_id,
                operation_type=operation_type,
                operation_table=operation_table,
                operation_content=operation_content,
                **kwargs
            )
        except Exception as e:
            logger.error(f"记录操作日志失败: {e}")
    
    @staticmethod
    def validate_required_fields(data, required_fields):
        """验证必需字段"""
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"缺少必需字段: {field}"
        return True, ""
    
    @staticmethod
    def validate_string_length(value, field_name, max_length, min_length=1):
        """验证字符串长度"""
        if not value or len(value) < min_length:
            return False, f"{field_name}不能为空"
        if len(value) > max_length:
            return False, f"{field_name}长度不能超过{max_length}个字符"
        return True, ""