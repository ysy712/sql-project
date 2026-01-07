from models.base_model import db, BaseModel
from datetime import datetime

class Resource(BaseModel):
    """林草资源信息模型"""
    __tablename__ = 'Resource'

    ResourceID = db.Column(db.String(32), primary_key=True, comment='资源编号')
    ResourceType = db.Column(db.String(10), nullable=False, comment='资源类型：树木/草地')
    AreaID = db.Column(db.String(15), db.ForeignKey('Area.AreaID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, comment='区域编号')
    SpeciesName = db.Column(db.String(50), nullable=False, comment='品种名称')
    Quantity = db.Column(db.Integer, comment='树木数量')
    Area = db.Column(db.Float, comment='草地面积')
    GrowthStatus = db.Column(db.String(16), nullable=False, comment='生长状态：幼苗/成长期/成熟期')
    PlantTime = db.Column(db.DateTime, nullable=False, comment='种植时间')
    UpdateTime = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    changes = db.relationship('ResourceChangeLog', backref='resource', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Resource {self.ResourceID} {self.ResourceType}>'

class ResourceChangeLog(BaseModel):
    """资源变动记录模型"""
    __tablename__ = 'ResourceChangeLog'

    ChangeID = db.Column(db.String(32), primary_key=True, comment='变动编号')
    ResourceID = db.Column(db.String(32), db.ForeignKey('Resource.ResourceID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, comment='资源编号')
    ChangeType = db.Column(db.String(16), nullable=False, comment='变动类型：新增/减少/状态更新')
    ChangeReason = db.Column(db.String(128), comment='变动原因')
    ChangeTime = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='变动时间')
    OperatorID = db.Column(db.String(15), db.ForeignKey('User.UserID', ondelete='RESTRICT', onupdate='CASCADE'), nullable=False, comment='操作人ID')

    def __repr__(self):
        return f'<ResourceChangeLog {self.ChangeID}>'