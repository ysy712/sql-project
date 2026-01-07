"""测试数据初始化脚本"""
from utils.db_utils import DBUtils

# 插入测试区域
def init_area():
    sql = "INSERT INTO area (id, name, parent_id, description) VALUES (1, '森林A区', 0, '核心监测区')"
    DBUtils.execute_update(sql)

# 插入测试传感器
def init_sensor():
    sql = """
    INSERT INTO sensor (sensor_code, name, type, area_id, location, status)
    VALUES 
    ('SN001', '温度传感器-森林A区', 'temperature', 1, '森林A区1号监测点', 'online'),
    ('SN002', '湿度传感器-森林A区', 'humidity', 1, '森林A区1号监测点', 'online'),
    ('SN003', '烟雾传感器-草地B区', 'smoke', 2, '草地B区2号监测点', 'offline')
    """
    DBUtils.execute_update(sql)

# 插入测试监测数据
def init_sensor_data():
    sql = """
    INSERT INTO sensor_data (sensor_id, value, unit, collect_time)
    VALUES 
    (1, 25.6, '℃', '2026-01-05 10:00:00'),
    (1, 26.2, '℃', '2026-01-05 11:00:00'),
    (2, 65.3, '%', '2026-01-05 10:00:00'),
    (2, 64.8, '%', '2026-01-05 11:00:00')
    """
    DBUtils.execute_update(sql)

if __name__ == "__main__":
    try:
        init_area()
        init_sensor()
        init_sensor_data()
        print("测试数据初始化成功！")
    except Exception as e:
        print(f"初始化失败：{e}")