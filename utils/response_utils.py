# utils/response_utils.py
from typing import Any, Dict, Optional
from enum import Enum
from flask import jsonify


class ResponseCode(Enum):
    """响应状态码枚举"""
    SUCCESS = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


class ResponseModel:
    """统一响应模型（兼容旧名称）"""
    
    def __init__(self, code: int, message: str = "", data: Any = None, total: int = None):
        self.code = code
        self.message = message
        self.data = data
        self.total = total
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
        
        if self.total is not None:
            result["total"] = self.total
        
        return result
    
    def to_json(self):
        """转换为JSON响应"""
        return jsonify(self.to_dict())


# 为兼容性，创建别名
ApiResponse = ResponseModel


def success_response(data: Any = None, message: str = "操作成功", total: int = None) -> Dict[str, Any]:
    """成功响应"""
    return ResponseModel(
        code=ResponseCode.SUCCESS.value,
        message=message,
        data=data,
        total=total
    ).to_dict()


def error_response(code: int = ResponseCode.BAD_REQUEST.value, 
                   message: str = "操作失败", data: Any = None) -> Dict[str, Any]:
    """错误响应"""
    return ResponseModel(
        code=code,
        message=message,
        data=data
    ).to_dict()


def pagination_response(items: list, total: int, page: int, per_page: int) -> Dict[str, Any]:
    """分页响应"""
    return success_response(
        data={
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        },
        total=total
    )