# api/device.py
"""
设备管理API模块
"""
from flask import jsonify
from . import device_bp


@device_bp.route('')
def get_devices():
    """获取设备列表"""
    return jsonify({
        'code': 200,
        'message': "设备管理功能暂未实现",
        'data': []
    })


@device_bp.route('/<device_id>')
def get_device_detail(device_id):
    """获取设备详情"""
    return jsonify({
        'code': 200,
        'message': "设备详情",
        'data': {
            'id': device_id,
            'status': '未实现'
        }
    })