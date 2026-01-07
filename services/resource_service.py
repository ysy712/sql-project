# resource_service.py
from datetime import datetime
from typing import Dict, Any, List, Optional
from models import db
from models.resource_model import Resource, ResourceChangeLog
from models.sensor_model import Area
from .base_service import BaseService

class ResourceService(BaseService):
    """资源信息服务"""
    def __init__(self):
        super().__init__(Resource)

    def get_resources_by_area(self, area_id: str) -> List[Dict[str, Any]]:
        """根据区域ID获取资源列表"""
        resources = self.model_class.query.filter_by(AreaID=area_id).all()  # 改为 model_class
        return [r.to_dict() for r in resources]

    def get_resource_statistics(self, area_id: Optional[str] = None) -> Dict[str, Any]:
        """统计资源信息（可按区域、类型、生长状态）"""
        query = self.model_class.query  # 改为 model_class
        if area_id:
            query = query.filter_by(AreaID=area_id)
        total = query.count()
        tree_count = query.filter_by(ResourceType='树木').count()
        grass_count = query.filter_by(ResourceType='草地').count()
        status_stats = {}
        for status in ['幼苗', '成长期', '成熟期']:
            status_stats[status] = query.filter_by(GrowthStatus=status).count()
        return {
            'total': total,
            'tree_count': tree_count,
            'grass_count': grass_count,
            'status_stats': status_stats
        }

    def create_resource(self, data: Dict[str, Any]) -> Resource:
        """创建资源信息"""
        data['UpdateTime'] = datetime.now()
        return self.create(data)

    def update_resource(self, resource_id: str, data: Dict[str, Any]) -> bool:
        """更新资源信息"""
        data['UpdateTime'] = datetime.now()
        instance = self.update(resource_id, data)
        return instance is not None

    def batch_update_resources(self, resource_list: List[Dict[str, Any]]) -> List[Resource]:
        """批量更新资源信息"""
        updated = []
        for item in resource_list:
            rid = item.get('ResourceID')
            if rid:
                self.update_resource(rid, item)
                updated.append(self.get_by_id(rid))
        return updated

class ResourceChangeLogService(BaseService):
    """资源变动记录服务"""
    def __init__(self):
        super().__init__(ResourceChangeLog)

    def create_change_log(self, data: Dict[str, Any]) -> ResourceChangeLog:
        """创建资源变动记录"""
        data['ChangeTime'] = datetime.now()
        return self.create(data)

    def get_changes_by_resource(self, resource_id: str) -> List[Dict[str, Any]]:
        """获取某资源的所有变动记录"""
        changes = self.model_class.query.filter_by(ResourceID=resource_id).order_by(ResourceChangeLog.ChangeTime.desc()).all()
        return [c.to_dict() for c in changes]

    def get_changes_by_operator(self, operator_id: str) -> List[Dict[str, Any]]:
        """获取某操作人的所有变动记录"""
        changes = self.model_class.query.filter_by(OperatorID=operator_id).order_by(ResourceChangeLog.ChangeTime.desc()).all()
        return [c.to_dict() for c in changes]