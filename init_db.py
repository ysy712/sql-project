# init_db.py
from flask import Flask
from config import config
from models import db
from models.sensor_model import Area, Sensor, Monitor
from datetime import datetime, timedelta
import random
import os
import bcrypt
from sqlalchemy import text  # 导入 text

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config)
    config.init_app(app)

    db.init_app(app)

    return app

def hash_password(password):
    """哈希密码"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def init_database():
    """初始化数据库"""
    print("初始化数据库...")

    app = create_app()

    with app.app_context():
        try:
            # 删除所有表
            print("删除现有表...")
            db.drop_all()

            # 创建所有表
            print("创建新表...")
            db.create_all()
            print("✓ 数据库表创建成功")

            # 插入测试数据
            print("添加测试数据...")
            insert_test_data()

            return True

        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            return False

def insert_test_data():
    """插入测试数据"""
    try:
        print("添加区域数据...")

        # 添加测试区域
        areas = [
            Area(
                AreaID='AREA-FOR-001',
                AreaName='森林保护区A区',
                AreaType='森林',
                Location='39.9042,116.4074',
                CreatedTime=datetime.now()
            ),
            Area(
                AreaID='AREA-GRA-001',
                AreaName='草地示范区B区',
                AreaType='草地',
                Location='31.2304,121.4737',
                CreatedTime=datetime.now()
            ),
            Area(
                AreaID='AREA-FOR-002',
                AreaName='森林保护区B区',
                AreaType='森林',
                Location='40.7128,-74.0060',
                CreatedTime=datetime.now()
            )
        ]

        db.session.add_all(areas)
        db.session.commit()
        print(f"✓ 添加了 {len(areas)} 个区域")

        # 添加用户表测试数据
        print("添加用户数据...")
        
        # 注意：为了确保测试数据与你提供的数据完全一致，使用你提供的哈希密码
        users_sql = text("""
        INSERT INTO `user` (`UserID`, `Username`, `Password`, `Gender`, `Email`, `RoleType`, `AreaID`, `CreatedTime`, `UpdatedTime`, `IsActive`) VALUES
        ('USR-FLD-001', 'ranger_wu', '$2b$12$zeKO6qlN7HglWXmvIJ..peTG30PxyOAN8LyKCE4csbKD7ZAQ/z4B6', '未知', 'wu@example.com', '区域护林员', 'AREA-FOR-001', '2026-01-07 08:14:17', '2026-01-07 10:25:58', 1),
        ('USR-PUB-001', 'public_1', '$2b$12$/a0XV3xNowIGNQtDQAH3RupFlXUSebYa1TdM8ZZ1gbfKzhDGGmGSe', '男', 'public1@example.com', '公众用户', NULL, '2026-01-07 10:28:20', '2026-01-07 10:28:20', 1),
        ('USR-SYS-001', 'admin_zhang', '$2b$12$OralPMgR/zbSdFa0IjC9L.yRdvB0pmsAYf.uJHy4jFVI9vu//jPjy', '男', 'zhang@bfu.edu.cn', '系统管理员', NULL, '2026-01-05 17:50:09', '2026-01-06 17:03:25', 1),
        ('USR-SYS-002', 'test_admin', '$2b$12$KZC5isWX2cTzn3LZyos0hOPGOJC17H6WVF9sKsLki67LQp.W3EQRS', '男', 'test@example.com', '系统管理员', NULL, '2026-01-06 10:00:00', '2026-01-06 10:00:00', 1),
        ('USR-SYS-003', 'admin_li', '$2b$12$VTOBphpbdijQRGM9/Hug7.HkVO8kaJhAjPOWh6SqC6kxPGruA5qCS', '女', 'li@example.com', '系统管理员', NULL, '2026-01-07 08:04:09', '2026-01-07 08:06:03', 1);
        """)
        
        db.session.execute(users_sql)
        db.session.commit()
        print(f"✓ 添加了 5 个用户")

        # 添加更多用户测试数据（可选）
        print("添加更多用户测试数据...")
        
        # 生成新密码进行哈希
        data_password = hash_password('123456')
        field_password = hash_password('123456')
        supervisor_password = hash_password('123456')
        public_password = hash_password('123456')
        data_password2 = hash_password('123456')
        
        additional_users_sql = text(f"""
        INSERT INTO `user` (`UserID`, `Username`, `Password`, `Gender`, `Email`, `RoleType`, `AreaID`, `CreatedTime`, `UpdatedTime`, `IsActive`) VALUES
        ('USR-DATA-001', 'data_manager', '{data_password}', '女', 'data@example.com', '数据管理员', NULL, '2026-01-07 11:00:00', '2026-01-07 11:00:00', 1),
        ('USR-FLD-002', 'ranger_li', '{field_password}', '男', 'li_ranger@example.com', '区域护林员', 'AREA-FOR-002', '2026-01-07 11:10:00', '2026-01-07 11:10:00', 1),
        ('USR-SUP-001', 'supervisor_wang', '{supervisor_password}', '男', 'wang@example.com', '监管人员', NULL, '2026-01-07 11:20:00', '2026-01-07 11:20:00', 1),
        ('USR-PUB-002', 'public_2', '{public_password}', '女', 'public2@example.com', '公众用户', NULL, '2026-01-07 11:30:00', '2026-01-07 11:30:00', 1),
        ('USR-DATA-002', 'data_admin2', '{data_password2}', '男', 'data2@example.com', '数据管理员', NULL, '2026-01-07 11:40:00', '2026-01-07 11:40:00', 1);
        """)
        
        db.session.execute(additional_users_sql)
        db.session.commit()
        print(f"✓ 添加了 5 个额外用户")

        # 添加测试传感器
        print("添加传感器数据...")
        sensors = [
            Sensor(
                SensorID='SENSOR-TEMP-001',
                AreaID='AREA-FOR-001',
                DeviceModel='DHT22',
                MonitorType='温度',
                InstallTime=datetime.now(),
                Protocol='MQTT'
            ),
            Sensor(
                SensorID='SENSOR-HUM-001',
                AreaID='AREA-FOR-001',
                DeviceModel='DHT22',
                MonitorType='湿度',
                InstallTime=datetime.now(),
                Protocol='MQTT'
            ),
            Sensor(
                SensorID='SENSOR-IMG-001',
                AreaID='AREA-GRA-001',
                DeviceModel='摄像头V3',
                MonitorType='图像',
                InstallTime=datetime.now(),
                Protocol='HTTP'
            ),
            Sensor(
                SensorID='SENSOR-TEMP-002',
                AreaID='AREA-FOR-002',
                DeviceModel='DHT11',
                MonitorType='温度',
                InstallTime=datetime.now(),
                Protocol='MQTT'
            ),
            Sensor(
                SensorID='SENSOR-HUM-002',
                AreaID='AREA-FOR-002',
                DeviceModel='DHT11',
                MonitorType='湿度',
                InstallTime=datetime.now(),
                Protocol='MQTT'
            )
        ]

        db.session.add_all(sensors)
        db.session.commit()
        print(f"✓ 添加了 {len(sensors)} 个传感器")

        # 添加测试监测数据
        print("添加监测数据...")
        monitor_data = []
        base_time = datetime.now() - timedelta(hours=24)

        for sensor in sensors:
            for i in range(20):  # 每个传感器添加20条测试数据
                collect_time = base_time + timedelta(hours=i)

                if sensor.MonitorType == '温度':
                    value = f"{round(random.uniform(15, 35), 1)}°C"
                elif sensor.MonitorType == '湿度':
                    value = f"{random.randint(40, 90)}%"
                else:
                    value = f"/static/images/sample_{random.randint(1, 5)}.jpg"

                monitor = Monitor(
                    CollectTime=collect_time,
                    SensorID=sensor.SensorID,
                    MonitorValue=value,
                    DataStatus='有效' if random.random() > 0.1 else '无效'
                )
                monitor_data.append(monitor)

        db.session.add_all(monitor_data)
        db.session.commit()
        print(f"✓ 添加了 {len(monitor_data)} 条监测数据")

        print("✅ 测试数据插入完成！")

    except Exception as e:
        db.session.rollback()
        print(f"✗ 插入测试数据失败: {e}")
        import traceback
        traceback.print_exc()
        raise

def check_database():
    """检查数据库状态"""
    app = create_app()

    with app.app_context():
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            print(f"\n数据库中有 {len(tables)} 个表:")
            for table in tables:
                print(f"  - {table}")

            # 统计各表数据量
            try:
                area_count = Area.query.count()
                sensor_count = Sensor.query.count()
                monitor_count = Monitor.query.count()
                
                # 尝试统计用户数量
                user_count_result = db.session.execute(text("SELECT COUNT(*) FROM `user`")).fetchone()
                user_count = user_count_result[0] if user_count_result else 0

                print(f"\n数据统计:")
                print(f"  用户数量: {user_count}")
                print(f"  区域数量: {area_count}")
                print(f"  传感器数量: {sensor_count}")
                print(f"  监测数据数量: {monitor_count}")

                # 显示用户详情
                print(f"\n用户详情:")
                users_result = db.session.execute(text("SELECT UserID, Username, RoleType, AreaID FROM `user` WHERE IsActive = 1")).fetchall()
                for user in users_result:
                    area_info = f" (区域: {user[3]})" if user[3] else ""
                    print(f"  - {user[0]}: {user[1]} [{user[2]}]{area_info}")

            except Exception as e:
                print(f"  数据统计时出现错误: {e}")
                import traceback
                traceback.print_exc()

            return True

        except Exception as e:
            print(f"检查数据库失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("=" * 60)
    print("智慧林草监测系统 - 数据库初始化")
    print("=" * 60)

    # 导入用户模型以确保表被创建
    try:
        from models.user_model import UserModel
        print("✓ 用户模型导入成功")
    except ImportError as e:
        print(f"⚠ 用户模型导入警告: {e}")
        print("⚠ 用户表可能无法正常创建")
    
    if init_database():
        print("\n✅ 数据库初始化成功！")

        # 检查数据库状态
        print("\n📊 数据库状态:")
        check_database()

        print("\n" + "=" * 60)
        print("🎉 初始化完成！")
        print("\n运行以下命令启动系统:")
        print("python main.py")
        print("\n然后访问: http://localhost:5000")
        print("=" * 60)
    else:
        print("\n❌ 数据库初始化失败！")