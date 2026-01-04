from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ResponseCode(Enum):
    """响应码枚举"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500

@dataclass
class ApiResponse:
    """统一API响应格式"""
    code: int
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'code': self.code,
            'message': self.message,
            'timestamp': self._get_timestamp()
        }
        
        if self.data is not None:
            result['data'] = self.data
        
        if self.total is not None:
            result['total'] = self.total
        
        return result
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False)
    
    @staticmethod
    def _get_timestamp() -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()

def success_response(data: Any = None, message: str = "操作成功", total: int = None) -> Dict[str, Any]:
    """成功响应"""
    response = ApiResponse(
        code=ResponseCode.SUCCESS.value,
        message=message,
        data=data,
        total=total
    )
    return response.to_dict()

def created_response(data: Any = None, message: str = "创建成功") -> Dict[str, Any]:
    """创建成功响应"""
    response = ApiResponse(
        code=ResponseCode.CREATED.value,
        message=message,
        data=data
    )
    return response.to_dict()

def error_response(code: int, message: str, data: Any = None) -> Dict[str, Any]:
    """错误响应"""
    response = ApiResponse(
        code=code,
        message=message,
        data=data
    )
    return response.to_dict()

def bad_request_response(message: str = "请求参数错误") -> Dict[str, Any]:
    """400错误响应"""
    return error_response(ResponseCode.BAD_REQUEST.value, message)

def unauthorized_response(message: str = "未授权访问") -> Dict[str, Any]:
    """401错误响应"""
    return error_response(ResponseCode.UNAUTHORIZED.value, message)

def forbidden_response(message: str = "禁止访问") -> Dict[str, Any]:
    """403错误响应"""
    return error_response(ResponseCode.FORBIDDEN.value, message)

def not_found_response(message: str = "资源未找到") -> Dict[str, Any]:
    """404错误响应"""
    return error_response(ResponseCode.NOT_FOUND.value, message)

def internal_error_response(message: str = "服务器内部错误") -> Dict[str, Any]:
    """500错误响应"""
    return error_response(ResponseCode.INTERNAL_ERROR.value, message)