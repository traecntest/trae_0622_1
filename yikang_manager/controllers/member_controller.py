"""
颐康管家 - 家庭成员控制器
协调家庭成员档案的增删改查与树形关系构建。
"""
from models.family_member import FamilyMember
from models.health_record import HealthRecord
from models.medication import Medication
from models.medical_history import MedicalHistory


class MemberController:
    """家庭成员管理控制器。"""

    def get_all_members(self):
        return FamilyMember.all()

    def get_member(self, member_id):
        return FamilyMember.get(member_id)

    def save_member(self, data):
        member = FamilyMember(**data)
        member.save()
        return member

    def delete_member(self, member_id):
        member = FamilyMember.get(member_id)
        if member:
            return member.delete()
        return 0

    def search_members(self, keyword):
        if not keyword.strip():
            return FamilyMember.all()
        return FamilyMember.search(keyword)

    def build_family_tree(self):
        """构建家庭成员树形结构，返回根节点列表。
        每个节点: {"member": FamilyMember, "children": [...]}
        """
        all_members = FamilyMember.all()
        roots = [m for m in all_members if m.parent_id is None]
        for root in roots:
            self._build_children(root, all_members)
        if not roots and all_members:
            roots = all_members[:1]
            for r in roots:
                self._build_children(r, all_members)
        return roots

    def _build_children(self, parent, all_members):
        parent._tree_children = [
            m for m in all_members if m.parent_id == parent.id
        ]
        for child in parent._tree_children:
            self._build_children(child, all_members)

    def get_member_summary(self, member_id):
        """获取成员健康摘要信息。"""
        records = HealthRecord.by_member(member_id)
        meds = Medication.by_member(member_id)
        history = MedicalHistory.by_member(member_id)
        abnormal = HealthRecord.abnormal_count(member_id)
        latest_date = max((r.record_date for r in records), default="无")
        return {
            "record_count": len(records),
            "medication_count": len(meds),
            "history_count": len(history),
            "abnormal_count": abnormal,
            "latest_record_date": latest_date,
        }
