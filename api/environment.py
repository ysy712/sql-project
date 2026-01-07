from flask import request, jsonify
from datetime import datetime
from urllib.parse import unquote
from . import environment_bp
from services.sensor_service import AreaService, SensorService, MonitorService
from utils.response_utils import success_response, error_response, pagination_response
from utils.db_utils import transaction

# 初始化服务
area_service = AreaService()
sensor_service = SensorService()
monitor_service = MonitorService()


# ========== 区域管理接口 ==========

@environment_bp.route('/areas', methods=['GET'])
def get_areas():
    """获取区域列表（分页）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        area_type = request.args.get('area_type')

        filters = {}
        if area_type:
            filters['AreaType'] = area_type

        result = area_service.get_all(page=page, per_page=per_page, **filters)
        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas', methods=['POST'])
def create_area():
    """创建新区域"""
    try:
        data = request.get_json()

        # 必填字段验证
        required_fields = ['AreaID', 'AreaName', 'AreaType', 'Location']
        for field in required_fields:
            if field not in data:
                return jsonify(error_response(message=f"缺少必要字段: {field}")), 400

        # 区域类型验证
        if data['AreaType'] not in ['森林', '草地']:
            return jsonify(error_response(message="区域类型必须是'森林'或'草地'")), 400

        # 检查ID是否已存在
        existing_area = area_service.get_by_id(data['AreaID'])
        if existing_area:
            return jsonify(error_response(message=f"区域ID {data['AreaID']} 已存在")), 400

        # 创建区域
        area = area_service.create(data)
        return jsonify(success_response(area.to_dict(), "区域创建成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas/<area_id>', methods=['GET'])
def get_area_detail(area_id):
    """获取区域详情"""
    try:
        area = area_service.get_by_id(area_id)
        if not area:
            return jsonify(error_response(message=f"区域 {area_id} 不存在")), 404

        result = area.to_dict()

        # 添加传感器信息
        sensors = sensor_service.get_sensors_by_area(area_id)
        result['sensors'] = sensors
        result['sensor_count'] = len(sensors)

        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas/<area_id>', methods=['PUT'])
def update_area(area_id):
    """更新区域信息"""
    try:
        data = request.get_json()

        area = area_service.get_by_id(area_id)
        if not area:
            return jsonify(error_response(message=f"区域 {area_id} 不存在")), 404

        # 更新区域信息
        area_service.update(area_id, data)
        return jsonify(success_response(message="区域更新成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas/<area_id>', methods=['DELETE'])
def delete_area(area_id):
    """删除区域"""
    try:
        area = area_service.get_by_id(area_id)
        if not area:
            return jsonify(error_response(message=f"区域 {area_id} 不存在")), 404

        # 检查是否有传感器
        if len(area.sensors) > 0:
            return jsonify(error_response(message="该区域下存在传感器，无法删除")), 400

        area_service.delete(area_id)
        return jsonify(success_response(message="区域删除成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas/statistics', methods=['GET'])
def get_area_statistics():
    """获取区域统计信息"""
    try:
        statistics = area_service.get_area_statistics()
        return jsonify(success_response(statistics))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


# ========== 传感器管理接口 ==========

@environment_bp.route('/sensors', methods=['GET'])
def get_sensors():
    """获取传感器列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        area_id = request.args.get('area_id')
        monitor_type = request.args.get('monitor_type')

        filters = {}
        if area_id:
            filters['AreaID'] = area_id
        if monitor_type:
            filters['MonitorType'] = monitor_type

        result = sensor_service.get_all(page=page, per_page=per_page, **filters)
        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors', methods=['POST'])
def create_sensor():
    """创建新传感器"""
    try:
        data = request.get_json()

        # 必填字段验证
        required_fields = ['SensorID', 'AreaID', 'DeviceModel', 'MonitorType', 'InstallTime', 'Protocol']
        for field in required_fields:
            if field not in data:
                return jsonify(error_response(message=f"缺少必要字段: {field}")), 400

        # 监测类型验证
        if data['MonitorType'] not in ['温度', '湿度', '图像']:
            return jsonify(error_response(message="监测类型必须是'温度'、'湿度'或'图像'")), 400

        # 检查区域是否存在
        area = area_service.get_by_id(data['AreaID'])
        if not area:
            return jsonify(error_response(message=f"区域 {data['AreaID']} 不存在")), 400

        # 检查传感器ID是否已存在
        existing_sensor = sensor_service.get_by_id(data['SensorID'])
        if existing_sensor:
            return jsonify(error_response(message=f"传感器ID {data['SensorID']} 已存在")), 400

        # 转换InstallTime为datetime
        data['InstallTime'] = datetime.fromisoformat(data['InstallTime'].replace('Z', '+00:00'))

        # 创建传感器
        sensor = sensor_service.create(data)
        return jsonify(success_response(sensor.to_dict(), "传感器创建成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors/<sensor_id>', methods=['GET'])
def get_sensor_detail(sensor_id):
    """获取传感器详情"""
    try:
        sensor = sensor_service.get_by_id(sensor_id)
        if not sensor:
            return jsonify(error_response(message=f"传感器 {sensor_id} 不存在")), 404

        result = sensor.to_dict()

        # 添加区域信息
        area = area_service.get_by_id(sensor.AreaID)
        if area:
            result['area_info'] = {
                'AreaName': area.AreaName,
                'AreaType': area.AreaType,
                'Location': area.Location
            }

        # 添加最新监测数据
        latest_data = monitor_service.get_sensor_latest_data(sensor_id)
        if latest_data:
            result['latest_data'] = latest_data

        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors/<sensor_id>', methods=['DELETE'])
def delete_sensor(sensor_id):
    """删除传感器"""
    try:
        sensor = sensor_service.get_by_id(sensor_id)
        if not sensor:
            return jsonify(error_response(message=f"传感器 {sensor_id} 不存在")), 404

        # 检查是否有监测数据
        if len(sensor.monitors) > 0:
            return jsonify(error_response(message="该传感器存在监测数据，无法删除")), 400

        sensor_service.delete(sensor_id)
        return jsonify(success_response(message="传感器删除成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors/statistics', methods=['GET'])
def get_sensor_statistics():
    """获取传感器统计信息"""
    try:
        statistics = sensor_service.get_sensor_statistics()
        return jsonify(success_response(statistics))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


# ========== 监测数据接口 ==========

@environment_bp.route('/monitors', methods=['POST'])
def create_monitor_data():
    """创建监测数据"""
    try:
        data = request.get_json()

        # 必填字段验证
        required_fields = ['SensorID', 'MonitorValue']
        for field in required_fields:
            if field not in data:
                return jsonify(error_response(message=f"缺少必要字段: {field}")), 400

        # 检查传感器是否存在
        sensor = sensor_service.get_by_id(data['SensorID'])
        if not sensor:
            return jsonify(error_response(message=f"传感器 {data['SensorID']} 不存在")), 400

        # 设置数据状态（默认为有效），仅允许有效/无效
        data_status = data.get('DataStatus', '有效')
        if data_status not in ['有效', '无效']:
            data_status = '有效'

        # 创建监测数据（含自动有效性校验）
        monitor_data = monitor_service.create_monitor_data(
            sensor_id=data['SensorID'],
            value=data['MonitorValue'],
            data_status=data_status
        )

        # 直接使用创建后的对象（已刷新），避免再次查询精度差异
        return jsonify(success_response(monitor_data.to_dict(), "监测数据创建成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/monitors/batch', methods=['POST'])
def batch_create_monitor_data():
    """批量创建监测数据"""
    try:
        data_list = request.get_json()

        if not isinstance(data_list, list):
            return jsonify(error_response(message="请求数据必须是数组")), 400

        # 验证每个数据项
        valid_data = []
        sensor_ids = set()

        for data in data_list:
            required_fields = ['SensorID', 'MonitorValue']
            for field in required_fields:
                if field not in data:
                    return jsonify(error_response(message=f"缺少必要字段: {field}")), 400

            sensor_id = data['SensorID']
            sensor_ids.add(sensor_id)

            # 获取或缓存传感器，校验是否存在
            sensor = sensor_service.get_by_id(sensor_id)
            if not sensor:
                return jsonify(error_response(message=f"传感器 {sensor_id} 不存在")), 400

            # 自动校验监测值
            validated_status, normalized_value = monitor_service.validate_monitor_value(sensor.MonitorType, data['MonitorValue'])
            data_status = data.get('DataStatus', validated_status)
            if data_status not in ['有效', '无效'] or validated_status != '有效':
                data_status = validated_status

            valid_data.append({
                'SensorID': sensor_id,
                'MonitorValue': normalized_value,
                'DataStatus': data_status,
                'CollectTime': data.get('CollectTime', datetime.now())
            })

        # 批量创建数据（内部已处理校验）
        monitors = monitor_service.batch_create_monitor_data(valid_data)

        return jsonify(success_response(
            [monitor.to_dict() for monitor in monitors],
            f"成功创建 {len(monitors)} 条监测数据"
        ))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors/<sensor_id>/monitors', methods=['GET'])
def get_sensor_monitors(sensor_id):
    """获取传感器的监测数据"""
    try:
        # 检查传感器是否存在
        sensor = sensor_service.get_by_id(sensor_id)
        if not sensor:
            return jsonify(error_response(message=f"传感器 {sensor_id} 不存在")), 404

        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        data_status = request.args.get('data_status')

        # 构建查询
        filters = {'SensorID': sensor_id}

        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                filters['CollectTime'] = ('>=', start_dt)
            except ValueError:
                return jsonify(error_response(message="开始时间格式错误，请使用ISO格式")), 400

        if end_time:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                filters['CollectTime'] = ('<=', end_dt)
            except ValueError:
                return jsonify(error_response(message="结束时间格式错误，请使用ISO格式")), 400

        if data_status:
            filters['DataStatus'] = data_status

        # 获取数据
        result = monitor_service.get_all(page=page, per_page=per_page, **filters)

        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/sensors/<sensor_id>/monitors/recent', methods=['GET'])
def get_recent_monitors(sensor_id):
    """获取传感器最近的监测数据"""
    try:
        # 检查传感器是否存在
        sensor = sensor_service.get_by_id(sensor_id)
        if not sensor:
            return jsonify(error_response(message=f"传感器 {sensor_id} 不存在")), 404

        # 获取查询参数
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)

        # 限制最大查询范围
        if hours > 720:  # 30天
            hours = 720
        if limit > 1000:
            limit = 1000

        # 获取最近数据
        data = monitor_service.get_recent_data(sensor_id, hours=hours, limit=limit)

        return jsonify(success_response(data))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/monitors/<sensor_id>/<collect_time>', methods=['DELETE'])
def delete_monitor(sensor_id, collect_time):
    """删除指定时间点的监测数据"""
    try:
        collect_time_str = unquote(collect_time)
        try:
            collect_dt = datetime.fromisoformat(collect_time_str.replace('Z', '+00:00'))
        except ValueError:
            return jsonify(error_response(message="采集时间格式错误，请使用ISO格式")), 400

        deleted = monitor_service.delete_monitor(sensor_id, collect_dt)
        if not deleted:
            return jsonify(error_response(message="监测数据不存在")), 404

        return jsonify(success_response(message="监测数据删除成功"))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500


@environment_bp.route('/areas/<area_id>/dashboard', methods=['GET'])
def get_area_dashboard(area_id):
    """获取区域仪表板数据"""
    try:
        # 检查区域是否存在
        area = area_service.get_by_id(area_id)
        if not area:
            return jsonify(error_response(message=f"区域 {area_id} 不存在")), 404

        result = {
            'area_info': area.to_dict(),
            'sensors': [],
            'statistics': {
                'total_sensors': 0,
                'temperature_sensors': 0,
                'humidity_sensors': 0,
                'image_sensors': 0
            }
        }

        # 获取区域内的所有传感器
        sensors = sensor_service.get_sensors_by_area(area_id)
        result['sensors'] = sensors
        result['statistics']['total_sensors'] = len(sensors)

        # 统计传感器类型
        for sensor in sensors:
            if sensor['MonitorType'] == '温度':
                result['statistics']['temperature_sensors'] += 1
            elif sensor['MonitorType'] == '湿度':
                result['statistics']['humidity_sensors'] += 1
            elif sensor['MonitorType'] == '图像':
                result['statistics']['image_sensors'] += 1

            # 获取每个传感器的最新数据
            latest_data = monitor_service.get_sensor_latest_data(sensor['SensorID'])
            sensor['latest_data'] = latest_data

        return jsonify(success_response(result))
    except Exception as e:
        return jsonify(error_response(message=str(e))), 500

