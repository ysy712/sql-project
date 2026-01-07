# models/log_model.py
"""
系统操作日志模型模块
"""

from datetime import datetime, timedelta
from models import db
from .base_model import BaseModel
import re


class OperationLogModel(BaseModel):
    """系统操作日志模型（ORM版本）"""
    __tablename__ = 'OperationLog'
    
    # 操作结果常量
    RESULT_SUCCESS = '成功'
    RESULT_FAILURE = '失败'
    
    LogID = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='日志编号')
    UserID = db.Column(db.String(15), nullable=True, comment='用户编号')
    OperationType = db.Column(db.String(50), nullable=False, comment='操作类型')
    OperationTable = db.Column(db.String(50), nullable=True, comment='操作表名')
    OperationContent = db.Column(db.Text, nullable=True, comment='操作内容')
    IPAddress = db.Column(db.String(50), nullable=True, comment='IP地址')
    UserAgent = db.Column(db.String(255), nullable=True, comment='用户代理')
    Result = db.Column(db.String(10), default=RESULT_SUCCESS, comment='操作结果')
    ErrorMessage = db.Column(db.Text, nullable=True, comment='错误信息')
    CreatedTime = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    
    def __repr__(self):
        return f'<OperationLog {self.OperationType} {self.Result}>'
    
    # 兼容性方法
    @classmethod
    def create(cls, data: dict):
        """创建操作日志（兼容旧接口）"""
        instance = cls(**data)
        db.session.add(instance)
        db.session.commit()
        return instance.LogID
    
    @classmethod
    def log_operation(cls, user_id: str, operation_type: str, 
                     operation_table: str = None, operation_content: str = None,
                     ip_address: str = None, user_agent: str = None,
                     result: str = RESULT_SUCCESS, error_message: str = None):
        """记录操作日志"""
        log_data = {
            'UserID': user_id,
            'OperationType': operation_type,
            'OperationTable': operation_table,
            'OperationContent': operation_content,
            'IPAddress': ip_address,
            'UserAgent': user_agent,
            'Result': result,
            'ErrorMessage': error_message
        }
        
        instance = cls(**log_data)
        db.session.add(instance)
        db.session.commit()
        return instance.LogID
    
    @classmethod
    def get_user_logs(cls, user_id: str, days: int = 30, 
                     page: int = 1, page_size: int = 50):
        """获取用户的操作日志（兼容旧接口）"""
        start_time = datetime.now() - timedelta(days=days)
        
        query = cls.query.filter(
            cls.UserID == user_id,
            cls.CreatedTime >= start_time
        )
        
        pagination = query.order_by(cls.CreatedTime.desc()).paginate(
            page=page, per_page=page_size, error_out=False
        )
        
        return {
            'records': [item.to_dict() for item in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @classmethod
    def get_failed_logs(cls, days: int = 7, limit: int = 100):
        """获取失败的操作日志（兼容旧接口）"""
        start_time = datetime.now() - timedelta(days=days)
        
        logs = cls.query.filter(
            cls.Result == cls.RESULT_FAILURE,
            cls.CreatedTime >= start_time
        ).order_by(cls.CreatedTime.desc()).limit(limit).all()
        
        return [log.to_dict() for log in logs]
    
    @classmethod
    def get_operation_statistics(cls, start_time: datetime = None, 
                               end_time: datetime = None):
        """获取操作统计信息（兼容旧接口）"""
        from sqlalchemy import func, and_
        
        query = db.session.query(
            cls.OperationType,
            cls.Result,
            func.count().label('operation_count'),
            func.count(func.distinct(cls.UserID)).label('user_count')
        )
        
        conditions = []
        if start_time:
            conditions.append(cls.CreatedTime >= start_time)
        if end_time:
            conditions.append(cls.CreatedTime <= end_time)
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        results = query.group_by(cls.OperationType, cls.Result) \
                      .order_by(cls.OperationType, cls.Result) \
                      .all()
        
        stats = {
            'by_type': {},
            'by_result': {
                cls.RESULT_SUCCESS: 0,
                cls.RESULT_FAILURE: 0
            },
            'total': {
                'operations': 0,
                'users': set()
            }
        }
        
        for row in results:
            operation_type, result, operation_count, user_count = row
            
            # 按操作类型统计
            if operation_type not in stats['by_type']:
                stats['by_type'][operation_type] = {
                    cls.RESULT_SUCCESS: 0,
                    cls.RESULT_FAILURE: 0,
                    'total': 0
                }
            
            stats['by_type'][operation_type][result] = operation_count
            stats['by_type'][operation_type]['total'] += operation_count
            
            # 按结果统计
            stats['by_result'][result] += operation_count
            
            # 总统计
            stats['total']['operations'] += operation_count
        
        # 获取涉及的所有用户
        user_query = cls.query.with_entities(func.distinct(cls.UserID))
        if conditions:
            user_query = user_query.filter(and_(*conditions))
        user_query = user_query.filter(cls.UserID.isnot(None))
        
        user_results = user_query.all()
        for row in user_results:
            stats['total']['users'].add(row[0])
        
        return stats
    
    @classmethod
    def get_user_activity(cls, user_id: str, days: int = 30):
        """获取用户活动统计（兼容旧接口）"""
        from sqlalchemy import func, cast, Date
        
        start_time = datetime.now() - timedelta(days=days)
        
        results = db.session.query(
            func.date(cls.CreatedTime).label('date'),
            func.count().label('operation_count'),
            func.count(func.distinct(cls.OperationType)).label('operation_types'),
            func.sum(func.case((cls.Result == '成功', 1), else_=0)).label('success_count')
        ).filter(
            cls.UserID == user_id,
            cls.CreatedTime >= start_time
        ).group_by(func.date(cls.CreatedTime)) \
         .order_by('date') \
         .all()
        
        activity = {
            'dates': [],
            'operations': [],
            'success_rates': []
        }
        
        for row in results:
            date_str = row.date.strftime("%Y-%m-%d") if hasattr(row.date, 'strftime') else str(row.date)
            activity['dates'].append(date_str)
            activity['operations'].append(row.operation_count)
            
            if row.operation_count > 0:
                success_rate = row.success_count / row.operation_count * 100
                activity['success_rates'].append(round(success_rate, 2))
            else:
                activity['success_rates'].append(0)
        
        return activity
    
    @classmethod
    def clean_old_logs(cls, days: int = 365) -> int:
        """清理指定天数前的旧日志（兼容旧接口）"""
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = cls.query.filter(cls.CreatedTime < cutoff_time).delete()
        db.session.commit()
        return deleted_count
    
    @classmethod
    def validate_log_data(cls, data: dict) -> dict:
        """验证日志数据"""
        errors = {}
        
        # 验证操作类型
        if 'OperationType' in data:
            if not data['OperationType'] or len(data['OperationType']) > 50:
                errors['OperationType'] = '操作类型不能为空且长度不能超过50个字符'
        
        # 验证操作结果
        if 'Result' in data:
            valid_results = [cls.RESULT_SUCCESS, cls.RESULT_FAILURE]
            if data['Result'] not in valid_results:
                errors['Result'] = f'操作结果必须为: {", ".join(valid_results)}'
        
        # 验证用户ID
        if 'UserID' in data and data['UserID']:
            from .user_model import UserModel
            user = UserModel.find_by_id(data['UserID'])
            if not user:
                errors['UserID'] = '用户不存在'
        
        return errors