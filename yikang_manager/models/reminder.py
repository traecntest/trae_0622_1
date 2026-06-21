"""
颐康管家 - 提醒事项数据模型
"""
from database.db_manager import db


class Reminder:
    """提醒事项模型。"""

    TABLE = "reminders"

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.member_id = kwargs.get("member_id")
        self.title = kwargs.get("title", "")
        self.content = kwargs.get("content", "")
        self.remind_type = kwargs.get("remind_type", "复诊")
        self.remind_time = kwargs.get("remind_time", "")
        self.repeat_rule = kwargs.get("repeat_rule", "")
        self.is_done = kwargs.get("is_done", 0)
        self.created_at = kwargs.get("created_at", "")

    @classmethod
    def from_row(cls, row):
        return cls(**row) if row else None

    def save(self):
        data = {
            "member_id": self.member_id, "title": self.title,
            "content": self.content, "remind_type": self.remind_type,
            "remind_time": self.remind_time, "repeat_rule": self.repeat_rule,
            "is_done": self.is_done,
        }
        if self.id:
            db.update(self.TABLE, self.id, data)
        else:
            self.id = db.insert(self.TABLE, data)
        return self.id

    def mark_done(self, done=True):
        self.is_done = 1 if done else 0
        db.update(self.TABLE, self.id, {"is_done": self.is_done})

    def delete(self):
        if self.id:
            return db.delete(self.TABLE, self.id)
        return 0

    @classmethod
    def all(cls):
        rows = db.fetch_all(cls.TABLE)
        return [cls.from_row(r) for r in rows]

    @classmethod
    def pending(cls):
        rows = db.fetch_all(cls.TABLE, "is_done = 0", ())
        return [cls.from_row(r) for r in rows]

    @classmethod
    def by_member(cls, member_id):
        rows = db.fetch_all(cls.TABLE, "member_id = ?", (member_id,))
        return [cls.from_row(r) for r in rows]

    @classmethod
    def upcoming(cls, days=7):
        """获取未来N天内到期的提醒。"""
        sql = (
            "SELECT * FROM reminders WHERE is_done = 0 "
            "AND remind_time <= datetime('now', 'localtime', ?) "
            "ORDER BY remind_time"
        )
        rows = db.fetch_by_query(sql, (f"+{days} days",), table=cls.TABLE)
        return [cls.from_row(r) for r in rows]

    def to_dict(self):
        return {
            "id": self.id, "member_id": self.member_id, "title": self.title,
            "content": self.content, "remind_type": self.remind_type,
            "remind_time": self.remind_time, "repeat_rule": self.repeat_rule,
            "is_done": self.is_done, "created_at": self.created_at,
        }
