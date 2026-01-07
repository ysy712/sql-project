# api/resource.py
"""
资源管理API模块
"""
from flask import jsonify
from . import resource_bp


@resource_bp.route('')
def get_resources():
    """获取资源列表"""
    return jsonify({
        'code': 200,
        'message': "资源管理功能暂未实现",
        'data': []
    })


@resource_bp.route('/<resource_id>')
def get_resource_detail(resource_id):
    """获取资源详情"""
    return jsonify({
        'code': 200,
        'message': "资源详情",
        'data': {
            'id': resource_id,
            'status': '未实现'
        }
    })