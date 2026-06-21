"""
颐康管家 - 用药记录数据模型
"""
from database.db_manager import db


class Medication:
    """用药记录模型。"""

    TABLE = "medications"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.member_id = kwargs.get("member_id")
        self.drug_name = kwargs.get("drug_name", "")
        self.dosage = kwargs.get("dosage", "")
        self.frequency = kwargs.get("frequency", "")
        self.start_date = kwargs.get("start_date", "")
        self.end_date = kwargs.get("end_date", "")
        self.note = kwargs.get("note", "")
        self.created_at = kwargs.get("created_at", "")

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    def save(self):
        data = {
            "member_id": self.member_id, "drug_name": self.drug_name,
            "dosage": self.dosage, "frequency": self.frequency,
            "start_date": self.start_date, "end_date": self.end_date,
            "note": self.note,
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

    def to_dict(self):
        return {
            "id": self.id, "member_id": self.member_id,
            "drug_name": self.drug_name, "dosage": self.dosage,
            "frequency": self.frequency, "start_date": self.start_date,
            "end_date": self.end_date, "note": self.note,
            "created_at": self.created_at,
        }
