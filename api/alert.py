# api/alert.py
"""
灾害预警API模块
"""
from flask import jsonify
from . import alert_bp


@alert_bp.route('')
def get_alerts():
    """获取预警列表"""
    return jsonify({
        'code': 200,
        'message': "预警功能暂未实现",
        'data': []
    })


@alert_bp.route('/<alert_id>')
def get_alert_detail(alert_id):
    """获取预警详情"""
    return jsonify({
        'code': 200,
        'message': "预警详情",
        'data': {
            'id': alert_id,
            'status': '未实现'
        }
    })