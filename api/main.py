# api/main.py
"""
主API模块
处理系统状态、健康检查和其他通用接口
"""

from flask import jsonify
from datetime import datetime
from . import main_bp


@main_bp.route('/')
def index():
    """系统首页"""
    return jsonify({
        'code': 200,
        'message': "智慧林草系统 API 服务运行正常",
        'data': {
            'system': '智慧林草系统',
            'version': '1.0.0',
            'description': '森林和草地生态资源智能化管理平台',
            'timestamp': datetime.now().isoformat()
        }
    })


@main_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'code': 200,
        'message': "系统状态正常",
        'data': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }
    })


@main_bp.route('/test', methods=['GET'])
def test_endpoint():
    """测试接口"""
    return jsonify({
        'code': 200,
        'message': "测试成功",
        'data': {
            'timestamp': datetime.now().isoformat(),
            'message': '测试接口正常工作',
            'random_number': 42
        }
    })


@main_bp.route('/docs', methods=['GET'])
def api_documentation():
    """API文档"""
    return jsonify({
        'code': 200,
        'message': "API文档",
        'data': {
            'api_version': 'v1',
            'base_url': '/api',
            'endpoints': {
                'auth': {
                    'login': 'POST /api/auth/login',
                    'logout': 'POST /api/auth/logout',
                    'verify': 'GET /api/auth/verify'
                },
                'users': {
                    'list': 'GET /api/users',
                    'create': 'POST /api/users',
                    'detail': 'GET /api/users/{id}'
                },
                'environment': {
                    'areas': 'GET /api/environment/areas',
                    'sensors': 'GET /api/environment/sensors',
                    'monitors': 'GET /api/environment/monitors'
                }
            }
        }
    })