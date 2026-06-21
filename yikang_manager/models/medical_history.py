"""
颐康管家 - 病史记录数据模型
"""
from database.db_manager import db


class MedicalHistory:
    """病史记录模型。"""

    TABLE = "medical_history"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.member_id = kwargs.get("member_id")
        self.disease_name = kwargs.get("disease_name", "")
        self.diagnose_date = kwargs.get("diagnose_date", "")
        self.hospital = kwargs.get("hospital", "")
        self.status = kwargs.get("status", "治疗中")
        self.description = kwargs.get("description", "")
        self.created_at = kwargs.get("created_at", "")

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    def save(self):
        data = {
            "member_id": self.member_id, "disease_name": self.disease_name,
            "diagnose_date": self.diagnose_date, "hospital": self.hospital,
            "status": self.status, "description": self.description,
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

    @classmethod
    def by_member(cls, member_id):
        rows = db.fetch_all(cls.TABLE, "member_id = ?", (member_id,))
        return [cls.from_row(r) for r in rows]

    @classmethod
    def search(cls, keyword, member_id=None):
        sql = (
            "SELECT * FROM medical_history WHERE "
            "(disease_name LIKE ? OR hospital LIKE ? OR description LIKE ?)"
        )
        params = [f"%{keyword}%"] * 3
        if member_id:
            sql += " AND member_id = ?"
            params.append(member_id)
        sql += " ORDER BY diagnose_date DESC"
        rows = db.fetch_by_query(sql, tuple(params), table=cls.TABLE)
        return [cls.from_row(r) for r in rows]

    def to_dict(self):
        return {
            "id": self.id, "member_id": self.member_id,
            "disease_name": self.disease_name,
            "diagnose_date": self.diagnose_date, "hospital": self.hospital,
            "status": self.status, "description": self.description,
            "created_at": self.created_at,
        }
