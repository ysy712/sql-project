from typing import Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from models import db


def execute_raw_sql(sql: str, params: Dict[str, Any] = None) -> list:
    """执行原始SQL查询"""
    try:
        result = db.session.execute(sql, params or {})
        db.session.commit()

        if result.returns_rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []
    except SQLAlchemyError as e:
        db.session.rollback()
        raise e


def transaction(func):
    """事务装饰器"""

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise e

    return wrapper