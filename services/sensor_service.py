import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from models import db
from models.sensor_model import Area, Sensor, Monitor
from .base_service import BaseService


class AreaService(BaseService):
    """区域服务"""

    def __init__(self):
        super().__init__(Area)

    def get_area_statistics(self) -> Dict[str, Any]:
        """获取区域统计信息"""
        total_areas = self.count()
        forest_areas = self.count(AreaType='森林')
        grassland_areas = self.count(AreaType='草地')

        return {
            'total_areas': total_areas,
            'forest_areas': forest_areas,
            'grassland_areas': grassland_areas
        }

    def get_areas_with_sensors(self) -> List[Dict[str, Any]]:
        """获取包含传感器信息的区域列表"""
        areas = Area.query.all()
        result = []

        for area in areas:
            area_data = area.to_dict()
            sensor_count = len(area.sensors)
            area_data['sensor_count'] = sensor_count
            result.append(area_data)

        return result


class SensorService(BaseService):
    """传感器服务"""

    def __init__(self):
        super().__init__(Sensor)

    def get_sensors_by_area(self, area_id: str) -> List[Dict[str, Any]]:
        """根据区域ID获取传感器列表"""
        sensors = Sensor.query.filter_by(AreaID=area_id).all()
        return [sensor.to_dict() for sensor in sensors]

    def get_sensor_statistics(self) -> Dict[str, Any]:
        """获取传感器统计信息"""
        total_sensors = self.count()
        temp_sensors = self.count(MonitorType='温度')
        hum_sensors = self.count(MonitorType='湿度')
        img_sensors = self.count(MonitorType='图像')

        return {
            'total_sensors': total_sensors,
            'temperature_sensors': temp_sensors,
            'humidity_sensors': hum_sensors,
            'image_sensors': img_sensors
        }


class MonitorService(BaseService):
    """监测数据服务"""

    def __init__(self):
        super().__init__(Monitor)

    ALLOWED_STATUS = {'有效', '无效'}

    def validate_monitor_value(self, monitor_type: str, value: str) -> Tuple[str, str]:
        """根据监测类型校验监测值并返回状态与规范化后的值（无效将标记为“无效”）"""
        value_str = str(value).strip()

        # 提取数值部分（如"25.5°C"、"60%"）
        def extract_number(text: str) -> Optional[float]:
            match = re.search(r'[-+]?\d*\.?\d+', text)
            return float(match.group()) if match else None

        status = '有效'

        if monitor_type == '温度':
            num = extract_number(value_str)
            # 合理区间：-50°C ~ 70°C
            if num is None or num < -50 or num > 70:
                status = '无效'
        elif monitor_type == '湿度':
            num = extract_number(value_str)
            # 合理区间：0% ~ 100%
            if num is None or num < 0 or num > 100:
                status = '无效'
        elif monitor_type == '图像':
            # 图像类：只校验是否为空
            if not value_str:
                status = '无效'

        return status, value_str

    def get_recent_data(self, sensor_id: str, hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
        """获取传感器最近一段时间的数据

        Args:
            sensor_id: 传感器ID
            hours: 小时数，默认为24小时
            limit: 返回数量限制

        Returns:
            监测数据列表
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        data = Monitor.query.filter(
            Monitor.SensorID == sensor_id,
            Monitor.CollectTime >= start_time,
            Monitor.CollectTime <= end_time,
            Monitor.DataStatus == '有效'
        ).order_by(Monitor.CollectTime.desc()).limit(limit).all()

        return [item.to_dict() for item in data]

    def create_monitor_data(self, sensor_id: str, value: str, data_status: str = '有效') -> Monitor:
        """创建监测数据记录

        Args:
            sensor_id: 传感器ID
            value: 监测值
            data_status: 数据状态，默认为'有效'

        Returns:
            创建的监测记录
        """
        sensor = Sensor.query.get(sensor_id)
        if not sensor:
            raise ValueError(f"传感器 {sensor_id} 不存在")

        validated_status, normalized_value = self.validate_monitor_value(sensor.MonitorType, value)

        # 如果上送状态不合法，或校验为无效，则以校验结果为准
        if data_status not in self.ALLOWED_STATUS or validated_status != '有效':
            data_status = validated_status

        collect_time = datetime.now().replace(microsecond=0)

        monitor_data = {
            'SensorID': sensor_id,
            'MonitorValue': normalized_value,
            'DataStatus': data_status,
            'CollectTime': collect_time
        }

        return self.create(monitor_data)

    def get_sensor_latest_data(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """获取传感器最新一条数据"""
        data = Monitor.query.filter_by(SensorID=sensor_id, DataStatus='有效') \
            .order_by(Monitor.CollectTime.desc()) \
            .first()

        return data.to_dict() if data else None

    def batch_create_monitor_data(self, data_list: List[Dict[str, Any]]) -> List[Monitor]:
        """批量创建监测数据"""
        sensor_cache: Dict[str, Sensor] = {}
        prepared: List[Dict[str, Any]] = []

        for item in data_list:
            sensor_id = item['SensorID']
            sensor = sensor_cache.get(sensor_id)
            if sensor is None:
                sensor = Sensor.query.get(sensor_id)
                if not sensor:
                    raise ValueError(f"传感器 {sensor_id} 不存在")
                sensor_cache[sensor_id] = sensor

            validated_status, normalized_value = self.validate_monitor_value(sensor.MonitorType, item['MonitorValue'])
            data_status = item.get('DataStatus', validated_status)

            # 校验状态
            if data_status not in self.ALLOWED_STATUS or validated_status != '有效':
                data_status = validated_status

            collect_time = item.get('CollectTime', datetime.now())
            if isinstance(collect_time, datetime):
                collect_time = collect_time.replace(microsecond=0)

            prepared.append({
                'SensorID': sensor_id,
                'MonitorValue': normalized_value,
                'DataStatus': data_status,
                'CollectTime': collect_time
            })

        return self.bulk_create(prepared)

    def get_data_by_time_range(self, sensor_id: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """获取指定时间范围内的数据"""
        data = Monitor.query.filter(
            Monitor.SensorID == sensor_id,
            Monitor.CollectTime >= start_time,
            Monitor.CollectTime <= end_time,
        ).order_by(Monitor.CollectTime).all()

        return [item.to_dict() for item in data]

    def delete_monitor(self, sensor_id: str, collect_time: datetime) -> bool:
        """删除指定传感器在给定时间的监测数据"""
        record = Monitor.query.filter_by(SensorID=sensor_id, CollectTime=collect_time).first()
        if not record:
            return False

        db.session.delete(record)
        db.session.commit()
        return True

    def get_monitor(self, sensor_id: str, collect_time: datetime) -> Optional[Monitor]:
        """根据复合主键获取监测数据"""
        return Monitor.query.filter_by(SensorID=sensor_id, CollectTime=collect_time).first()