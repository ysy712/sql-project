# api/resource.py
print("📦 加载 resource.py 模块...")
from flask import jsonify, request
from datetime import datetime  # 这是正确的导入
import random
from . import resource_bp
from services.resource_service import ResourceService, ResourceChangeLogService

resource_service = ResourceService()
change_log_service = ResourceChangeLogService()

# 资源统计接口
@resource_bp.route('/statistics', methods=['GET'])
def get_resource_statistics():
    """获取资源统计信息（总数、树木、草地、生长状态）"""
    try:
        area_id = request.args.get('area_id')
        stats = resource_service.get_resource_statistics(area_id)
        return jsonify({
            'code': 200,
            'message': '资源统计',
            'data': stats
        })
    except Exception as e:
        print(f"❌ 获取资源统计失败: {e}")
        return jsonify({
            'code': 500,
            'message': f"获取资源统计失败: {str(e)}",
            'data': None
        }), 500

@resource_bp.route('', methods=['GET'])
def get_resources():
    """获取资源列表，可选按区域筛选"""
    try:
        area_id = request.args.get('area_id')
        
        if area_id:
            # 按区域筛选
            resources = resource_service.get_resources_by_area(area_id)
        else:
            # 获取所有资源
            resources = [r.to_dict() for r in resource_service.model_class.query.all()]
        
        return jsonify({
            'code': 200,
            'message': "资源列表",
            'data': resources
        })
    except Exception as e:
        print(f"❌ 获取资源列表失败: {e}")
        return jsonify({
            'code': 500,
            'message': f"获取资源列表失败: {str(e)}",
            'data': []
        }), 500

@resource_bp.route('/<resource_id>', methods=['GET'])
def get_resource_detail(resource_id):
    """获取资源详情"""
    try:
        resource = resource_service.get_by_id(resource_id)
        if not resource:
            return jsonify({'code': 404, 'message': '资源不存在', 'data': None}), 404
        return jsonify({
            'code': 200,
            'message': "资源详情",
            'data': resource.to_dict()
        })
    except Exception as e:
        print(f"❌ 获取资源详情失败: {e}")
        return jsonify({
            'code': 500,
            'message': f"获取资源详情失败: {str(e)}",
            'data': None
        }), 500

@resource_bp.route('/<resource_id>/changes', methods=['GET'])
def get_resource_changes(resource_id):
    """获取资源变动记录"""
    try:
        changes = change_log_service.get_changes_by_resource(resource_id)
        return jsonify({
            'code': 200,
            'message': "资源变动记录",
            'data': changes
        })
    except Exception as e:
        print(f"❌ 获取变动记录失败: {e}")
        return jsonify({
            'code': 500,
            'message': f"获取变动记录失败: {str(e)}",
            'data': []
        }), 500

@resource_bp.route('', methods=['POST'])
def create_resource():
    """新增资源"""
    try:
        data = request.json or {}
        print(f"📥 创建资源数据: {data}")
        
        # 验证必需字段
        required_fields = ['ResourceType', 'AreaID', 'SpeciesName', 'GrowthStatus', 'PlantTime']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'code': 400,
                    'message': f'缺少必需字段: {field}',
                    'data': None
                }), 400
        
        # 根据类型验证数量或面积
        if data['ResourceType'] == '树木':
            if 'Quantity' not in data or data['Quantity'] is None:
                return jsonify({
                    'code': 400,
                    'message': '树木资源需要指定数量',
                    'data': None
                }), 400
            data['Area'] = None
        else:  # 草地
            if 'Area' not in data or data['Area'] is None:
                return jsonify({
                    'code': 400,
                    'message': '草地资源需要指定面积',
                    'data': None
                }), 400
            data['Quantity'] = None
        
        # 设置更新时间
        data['UpdateTime'] = datetime.now()
        
        # 生成资源ID（如果未提供）
        if 'ResourceID' not in data or not data['ResourceID']:
            # 使用已经导入的datetime模块，不要重新定义
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_str = str(random.randint(100, 999))
            prefix = 'RES-TREE' if data['ResourceType'] == '树木' else 'RES-GRASS'
            data['ResourceID'] = f'{prefix}-{timestamp}-{random_str}'
        
        resource = resource_service.create_resource(data)
        return jsonify({
            'code': 201, 
            'message': '资源创建成功', 
            'data': resource.to_dict()
        })
    except Exception as e:
        print(f"❌ 创建资源失败: {e}")
        import traceback
        traceback.print_exc()  # 打印完整的堆栈跟踪
        return jsonify({
            'code': 500,
            'message': f"创建资源失败: {str(e)}",
            'data': None
        }), 500

@resource_bp.route('/<resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """更新资源信息"""
    try:
        data = request.json or {}
        print(f"📥 更新资源数据: {data}")
        
        # 设置更新时间
        data['UpdateTime'] = datetime.now()
        
        success = resource_service.update_resource(resource_id, data)
        if not success:
            return jsonify({'code': 404, 'message': '资源不存在', 'data': None}), 404
        
        # 获取更新后的资源
        updated_resource = resource_service.get_by_id(resource_id)
        return jsonify({
            'code': 200, 
            'message': '资源更新成功',
            'data': updated_resource.to_dict()
        })
    except Exception as e:
        print(f"❌ 更新资源失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f"更新资源失败: {str(e)}",
            'data': None
        }), 500

@resource_bp.route('/<resource_id>/change', methods=['POST'])
def create_resource_change(resource_id):
    """新增资源变动记录"""
    try:
        data = request.json or {}
        data['ResourceID'] = resource_id
        
        # 生成变动ID（如果未提供）
        if 'ChangeID' not in data or not data['ChangeID']:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            random_str = str(random.randint(100, 999))
            data['ChangeID'] = f'CHG-{timestamp}-{random_str}'
        
        change = change_log_service.create_change_log(data)
        return jsonify({
            'code': 201, 
            'message': '变动记录创建成功', 
            'data': change.to_dict()
        })
    except Exception as e:
        print(f"❌ 创建变动记录失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'code': 500,
            'message': f"创建变动记录失败: {str(e)}",
            'data': None
        }), 500

# 添加测试路由
@resource_bp.route('/test', methods=['GET'])
def test_api():
    """测试API连接"""
    try:
        # 测试查询
        count = resource_service.model_class.query.count()
        return jsonify({
            'code': 200,
            'message': '资源API连接正常',
            'data': {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'resource_count': count
            }
        })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'资源API连接异常: {str(e)}',
            'data': None
        }), 500