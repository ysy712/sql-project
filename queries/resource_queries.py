# queries/resource_queries.py
"""
资源管理相关SQL查询
"""
from sqlalchemy import text
from models import db

# 查询：按区域、类型、生长状态统计资源数量/面积
def get_resource_statistics_by_area(area_id=None, resource_type=None, growth_status=None):
    sql = """
    SELECT AreaID,
           ResourceType,
           GrowthStatus,
           COUNT(*) AS resource_count,
           SUM(CASE WHEN ResourceType='树木' THEN Quantity ELSE 0 END) AS total_quantity,
           SUM(CASE WHEN ResourceType='草地' THEN `Area` ELSE 0 END) AS total_area
      FROM Resource
     WHERE 1=1
    """
    params = {}
    if area_id:
        sql += " AND AreaID = :area_id"
        params['area_id'] = area_id
    if resource_type:
        sql += " AND ResourceType = :resource_type"
        params['resource_type'] = resource_type
    if growth_status:
        sql += " AND GrowthStatus = :growth_status"
        params['growth_status'] = growth_status
    sql += " GROUP BY AreaID, ResourceType, GrowthStatus"
    result = db.session.execute(text(sql), params)
    return [dict(row) for row in result]

# 查询：获取某资源的所有变动记录（按时间倒序）
def get_resource_change_logs(resource_id):
    sql = """
    SELECT * FROM ResourceChangeLog
     WHERE ResourceID = :resource_id
     ORDER BY ChangeTime DESC
    """
    result = db.session.execute(text(sql), {'resource_id': resource_id})
    return [dict(row) for row in result]

# 查询：批量插入资源（示例，实际建议用ORM批量插入）
def batch_insert_resources(resource_list):
    # resource_list: List[Dict]
    for res in resource_list:
        db.session.execute(text("""
            INSERT INTO Resource (ResourceID, ResourceType, AreaID, SpeciesName, Quantity, Area, GrowthStatus, PlantTime, UpdateTime)
            VALUES (:ResourceID, :ResourceType, :AreaID, :SpeciesName, :Quantity, :Area, :GrowthStatus, :PlantTime, :UpdateTime)
        """), res)
    db.session.commit()

# 查询：批量更新资源（示例）
def batch_update_resources(resource_list):
    for res in resource_list:
        db.session.execute(text("""
            UPDATE Resource SET
                ResourceType = :ResourceType,
                AreaID = :AreaID,
                SpeciesName = :SpeciesName,
                Quantity = :Quantity,
                Area = :Area,
                GrowthStatus = :GrowthStatus,
                PlantTime = :PlantTime,
                UpdateTime = :UpdateTime
            WHERE ResourceID = :ResourceID
        """), res)
    db.session.commit()
