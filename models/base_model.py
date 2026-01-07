from datetime import datetime
from models import db


class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True

    def to_dict(self, exclude=None):
        """将模型对象转换为字典

        Args:
            exclude: 要排除的字段列表

        Returns:
            dict: 对象字典
        """
        result = {}
        for column in self.__table__.columns:
            if exclude and column.name in exclude:
                continue

            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value

        return result

    @classmethod
    def create(cls, **kwargs):
        """创建新记录"""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, **kwargs):
        """更新记录"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()

    def delete(self):
        """删除记录"""
        db.session.delete(self)
        db.session.commit()