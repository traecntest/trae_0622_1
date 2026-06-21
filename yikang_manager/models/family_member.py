"""
颐康管家 - 家庭成员数据模型
封装家庭成员的 CRUD 操作与业务逻辑。
"""
from database.db_manager import db


class FamilyMember:
    """家庭成员档案模型。"""

    TABLE = "family_members"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name", "")
        self.gender = kwargs.get("gender", "")
        self.birth_date = kwargs.get("birth_date", "")
        self.id_card = kwargs.get("id_card", "")
        self.phone = kwargs.get("phone", "")
        self.relation = kwargs.get("relation", "")
        self.parent_id = kwargs.get("parent_id")
        self.blood_type = kwargs.get("blood_type", "")
        self.allergy = kwargs.get("allergy", "")
        self.note = kwargs.get("note", "")
        self.created_at = kwargs.get("created_at", "")

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    def save(self):
        data = {
            "name": self.name, "gender": self.gender, "birth_date": self.birth_date,
            "id_card": self.id_card, "phone": self.phone, "relation": self.relation,
            "parent_id": self.parent_id, "blood_type": self.blood_type,
            "allergy": self.allergy, "note": self.note,
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
    def get(cls, member_id):
        row = db.fetch_one(cls.TABLE, member_id)
        return cls.from_row(row)

    @classmethod
    def all(cls):
        rows = db.fetch_all(cls.TABLE)
        return [cls.from_row(r) for r in rows]

    @classmethod
    def children_of(cls, parent_id):
        rows = db.fetch_all(cls.TABLE, "parent_id = ?", (parent_id,))
        return [cls.from_row(r) for r in rows]

    @classmethod
    def search(cls, keyword):
        """模糊搜索家庭成员。"""
        sql = (
            "SELECT * FROM family_members WHERE name LIKE ? OR relation LIKE ? "
            "OR phone LIKE ? OR note LIKE ? ORDER BY id"
        )
        kw = f"%{keyword}%"
        rows = db.fetch_by_query(sql, (kw, kw, kw, kw), table=cls.TABLE)
        return [cls.from_row(r) for r in rows]

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "gender": self.gender,
            "birth_date": self.birth_date, "id_card": self.id_card,
            "phone": self.phone, "relation": self.relation,
            "parent_id": self.parent_id, "blood_type": self.blood_type,
            "allergy": self.allergy, "note": self.note,
            "created_at": self.created_at,
        }

    def age(self):
        if not self.birth_date:
            return ""
        try:
            from datetime import date
            parts = self.birth_date.replace("-", "/").split("/")
            birth = date(int(parts[0]), int(parts[1]), int(parts[2]))
            today = date.today()
            return today.year - birth.year - (
                (today.month, today.day) < (birth.month, birth.day)
            )
        except Exception:
            return ""
