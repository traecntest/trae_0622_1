"""
颐康管家 - 健康记录数据模型
封装体检记录的 CRUD 操作与指标正常值判断逻辑。
"""
from database.db_manager import db
from config import NORMAL_RANGES


class HealthRecord:
    """体检指标记录模型。"""

    TABLE = "health_records"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.member_id = kwargs.get("member_id")
        self.record_date = kwargs.get("record_date", "")
        self.category = kwargs.get("category", "")
        self.indicator_name = kwargs.get("indicator_name", "")
        self.indicator_value = kwargs.get("indicator_value", "")
        self.unit = kwargs.get("unit", "")
        self.reference_range = kwargs.get("reference_range", "")
        self.is_abnormal = kwargs.get("is_abnormal", 0)
        self.report_image = kwargs.get("report_image", "")
        self.note = kwargs.get("note", "")
        self.created_at = kwargs.get("created_at", "")

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    def save(self):
        self.is_abnormal = self.check_abnormal()
        data = {
            "member_id": self.member_id, "record_date": self.record_date,
            "category": self.category, "indicator_name": self.indicator_name,
            "indicator_value": self.indicator_value, "unit": self.unit,
            "reference_range": self.reference_range, "is_abnormal": self.is_abnormal,
            "report_image": self.report_image, "note": self.note,
        }
        if self.id:
            db.update(self.TABLE, self.id, data)
        else:
            self.id = db.insert(self.TABLE, data)
        return self.id

    def delete(self):
        if self.id:
            return db.delete(self.TABLE, self.id)
        return 0

    def check_abnormal(self):
        """根据正常参考范围判断指标是否异常。"""
        if not self.indicator_name or not self.indicator_value:
            return 0
        rng = NORMAL_RANGES.get(self.indicator_name)
        if not rng:
            return 0
        try:
            val = float(self.indicator_value)
            low, high, _ = rng
            return 1 if (val < low or val > high) else 0
        except (ValueError, TypeError):
            if isinstance(self.indicator_value, str):
                return 0 if "阴性" in self.indicator_value or "-" in self.indicator_value else 1
            return 0

    @classmethod
    def get(cls, record_id):
        row = db.fetch_one(cls.TABLE, record_id)
        return cls.from_row(row)

    @classmethod
    def by_member(cls, member_id):
        rows = db.fetch_all(
            cls.TABLE, "member_id = ?", (member_id,)
        )
        return [cls.from_row(r) for r in rows]

    @classmethod
    def by_member_indicator(cls, member_id, indicator_name):
        """获取某成员某指标的历年记录（按日期排序），用于趋势图。"""
        sql = (
            "SELECT * FROM health_records WHERE member_id = ? AND indicator_name = ? "
            "ORDER BY record_date"
        )
        rows = db.fetch_by_query(sql, (member_id, indicator_name), table=cls.TABLE)
        return [cls.from_row(r) for r in rows]

    @classmethod
    def indicators_by_member(cls, member_id):
        """获取某成员所有出现过的指标名称列表。"""
        sql = (
            "SELECT DISTINCT indicator_name FROM health_records "
            "WHERE member_id = ? ORDER BY indicator_name"
        )
        with db.get_cursor() as cursor:
            cursor.execute(sql, (member_id,))
            return [row[0] for row in cursor.fetchall()]

    @classmethod
    def search(cls, keyword, member_id=None):
        """模糊搜索健康记录（按指标名、日期、备注）。"""
        sql = (
            "SELECT * FROM health_records WHERE "
            "(indicator_name LIKE ? OR record_date LIKE ? OR note LIKE ? OR category LIKE ?)"
        )
        params = [f"%{keyword}%"] * 4
        if member_id:
            sql += " AND member_id = ?"
            params.append(member_id)
        sql += " ORDER BY record_date DESC"
        rows = db.fetch_by_query(sql, tuple(params), table=cls.TABLE)
        return [cls.from_row(r) for r in rows]

    @classmethod
    def abnormal_count(cls, member_id=None):
        """统计异常指标数量。"""
        sql = "SELECT COUNT(*) FROM health_records WHERE is_abnormal = 1"
        params = ()
        if member_id:
            sql += " AND member_id = ?"
            params = (member_id,)
        with db.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()[0]

    def to_dict(self):
        return {
            "id": self.id, "member_id": self.member_id,
            "record_date": self.record_date, "category": self.category,
            "indicator_name": self.indicator_name,
            "indicator_value": self.indicator_value, "unit": self.unit,
            "reference_range": self.reference_range,
            "is_abnormal": self.is_abnormal, "report_image": self.report_image,
            "note": self.note, "created_at": self.created_at,
        }
