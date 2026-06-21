"""
颐康管家 - 用药与病史控制器
"""
from models.medication import Medication
from models.medical_history import MedicalHistory


class MedicationController:
    """用药记录控制器。"""

    def get_by_member(self, member_id):
        return Medication.by_member(member_id)

    def save(self, data):
        med = Medication(**data)
        med.save()
        return med

    def delete(self, med_id):
        med = Medication.get(med_id) if hasattr(Medication, "get") else None
        if med:
            return med.delete()
        from database.db_manager import db
        return db.delete(Medication.TABLE, med_id)


class HistoryController:
    """病史记录控制器。"""

    def get_by_member(self, member_id):
        return MedicalHistory.by_member(member_id)

    def save(self, data):
        hist = MedicalHistory(**data)
        hist.save()
        return hist

    def delete(self, hist_id):
        from database.db_manager import db
        return db.delete(MedicalHistory.TABLE, hist_id)

    def search(self, keyword, member_id=None):
        return MedicalHistory.search(keyword, member_id)
