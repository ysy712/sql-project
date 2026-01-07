"""传感器相关复杂查询函数"""
from utils.db_utils import DBUtils

def get_sensor_data_trend(sensor_id: int, days: int = 7) -> list:
    """
    获取传感器数据趋势（按天统计）
    :param sensor_id: 传感器ID
    :param days: 统计天数（默认7天）
    :return: 趋势数据列表
    """
    sql = """
    SELECT 
        DATE(collect_time) as collect_date,
        AVG(value) as avg_value,
        MAX(value) as max_value,
        MIN(value) as min_value
    FROM sensor_data
    WHERE sensor_id = %s 
    AND collect_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
    GROUP BY DATE(collect_time)
    ORDER BY collect_date ASC
    """
    return DBUtils.execute_query(sql, (sensor_id, days))

def get_area_sensor_statistics(area_id: int) -> dict:
    """
    获取区域内传感器状态统计
    :param area_id: 区域ID
    :return: 统计结果
    """
    sql = """
    SELECT 
        status,
        COUNT(*) as count
    FROM sensor
    WHERE area_id = %s
    GROUP BY status
    """
    result = DBUtils.execute_query(sql, (area_id,))
    # 转换为字典格式，方便前端使用
    stats = {"online": 0, "offline": 0, "fault": 0}
    for item in result:
        stats[item["status"]] = item["count"]
    return stats