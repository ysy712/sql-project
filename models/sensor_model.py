from datetime import datetime
from models import db
from .base_model import BaseModel


class Area(BaseModel):
    """区域信息模型"""
    __tablename__ = 'Area'

    AreaID = db.Column(db.String(15), primary_key=True, comment='区域编号')
    AreaName = db.Column(db.String(50), nullable=False, comment='区域名称')
    AreaType = db.Column(db.String(10), nullable=False, comment='区域类型：森林/草地')
    Location = db.Column(db.String(50), nullable=False, comment='地理位置')
    ManagerID = db.Column(db.String(15), comment='负责人ID')
    CreatedTime = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    UpdatedTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    sensors = db.relationship('Sensor', backref='area', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Area {self.AreaName} ({self.AreaID})>'


class Sensor(BaseModel):
    """传感器模型"""
    __tablename__ = 'Sensor'

    SensorID = db.Column(db.String(20), primary_key=True, comment='传感器编号')
    AreaID = db.Column(db.String(15), db.ForeignKey('Area.AreaID', ondelete='RESTRICT', onupdate='CASCADE'),
                       nullable=False, comment='部署区域')
    DeviceModel = db.Column(db.String(50), nullable=False, comment='设备型号')
    MonitorType = db.Column(db.String(20), nullable=False, comment='监测类型：温度/湿度/图像')
    InstallTime = db.Column(db.DateTime, nullable=False, comment='安装时间')
    Protocol = db.Column(db.String(30), nullable=False, comment='通信协议')

    # 关系
    monitors = db.relationship('Monitor', backref='sensor', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Sensor {self.SensorID} ({self.MonitorType})>'


class Monitor(BaseModel):
    """监测数据模型"""
    __tablename__ = 'Monitor'

    CollectTime = db.Column(db.DateTime, primary_key=True, comment='数据采集时间')
    SensorID = db.Column(db.String(20), db.ForeignKey('Sensor.SensorID', ondelete='RESTRICT', onupdate='CASCADE'),
                         primary_key=True, comment='传感器编号')
    MonitorValue = db.Column(db.String(100), nullable=False, comment='监测值')
    DataStatus = db.Column(db.String(10), nullable=False, default='有效', comment='数据状态：有效/无效')

    __table_args__ = (
        db.Index('idx_monitor_sensorid_collecttime', 'SensorID', 'CollectTime'),
    )

    def __repr__(self):
        return f'<Monitor {self.SensorID} @ {self.CollectTime}>'