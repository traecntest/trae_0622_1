"""
颐康管家 - 健康记录控制器
协调体检记录管理与数据可视化所需的数据聚合。
"""
from models.health_record import HealthRecord
from config import NORMAL_RANGES, INDICATOR_CATEGORIES


class RecordController:
    """健康记录管理控制器。"""

    def get_records_by_member(self, member_id):
        return HealthRecord.by_member(member_id)

    def get_record(self, record_id):
        return HealthRecord.get(record_id)

    def save_record(self, data):
        record = HealthRecord(**data)
        record.save()
        return record

    def delete_record(self, record_id):
        record = HealthRecord.get(record_id)
        if record:
            return record.delete()
        return 0

    def search_records(self, keyword, member_id=None):
        if not keyword.strip():
            if member_id:
                return HealthRecord.by_member(member_id)
            return []
        return HealthRecord.search(keyword, member_id)

    def get_indicator_names(self, member_id):
        return HealthRecord.indicators_by_member(member_id)

    def get_trend_data(self, member_id, indicator_name):
        """获取某成员某指标的历年趋势数据，返回 (dates, values, ref_range)。"""
        records = HealthRecord.by_member_indicator(member_id, indicator_name)
        dates = [r.record_date for r in records]
        values = []
        for r in records:
            try:
                values.append(float(r.indicator_value))
            except (ValueError, TypeError):
                values.append(None)
        rng = NORMAL_RANGES.get(indicator_name)
        ref_range = rng if rng else (None, None, None)
        return dates, values, ref_range

    def get_all_indicators_with_category(self):
        """返回所有指标及其分类，供界面选择。"""
        return INDICATOR_CATEGORIES

    def get_latest_abnormal(self, member_id, limit=5):
        """获取最近的异常指标记录。"""
        sql = (
            "SELECT * FROM health_records WHERE member_id = ? AND is_abnormal = 1 "
            "ORDER BY record_date DESC LIMIT ?"
        )
        from database.db_manager import db
        rows = db.fetch_by_query(sql, (member_id, limit), table="health_records")
        return [HealthRecord.from_row(r) for r in rows]
