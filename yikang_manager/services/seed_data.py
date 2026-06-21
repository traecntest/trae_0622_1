"""
颐康管家 - 测试数据初始化模块
在系统首次启动时，自动注入测试数据，包含家庭成员档案、
历年体检指标、用药记录、提醒事项和病史，便于演示数据可视化趋势。
"""
from datetime import datetime, timedelta


def init_seed_data():
    """初始化测试数据（仅在数据库为空时执行）。"""
    from models.family_member import FamilyMember
    from models.health_record import HealthRecord
    from models.medication import Medication
    from models.reminder import Reminder
    from models.medical_history import MedicalHistory

    if FamilyMember.all():
        return False

    members = [
        {"name": "李建国", "gender": "男", "birth_date": "1958-03-15",
         "relation": "本人", "phone": "13912345678", "blood_type": "A型",
         "allergy": "青霉素", "note": "退休工程师，轻度高血压"},
        {"name": "王秀兰", "gender": "女", "birth_date": "1960-08-22",
         "relation": "配偶", "phone": "13987654321", "blood_type": "O型",
         "allergy": "无", "note": "退休教师，血糖偏高"},
        {"name": "李明", "gender": "男", "birth_date": "1988-12-05",
         "relation": "儿子", "phone": "13800138000", "blood_type": "A型",
         "allergy": "无", "note": "软件工程师，久坐办公"},
        {"name": "李小红", "gender": "女", "birth_date": "1992-06-18",
         "relation": "女儿", "phone": "13800138001", "blood_type": "O型",
         "allergy": "海鲜", "note": "护士"},
    ]
    member_ids = []
    for m in members:
        member = FamilyMember(**m)
        member.save()
        member_ids.append(member.id)

    _seed_health_records(member_ids)
    _seed_medications(member_ids)
    _seed_reminders(member_ids)
    _seed_medical_history(member_ids)
    return True


def _seed_health_records(member_ids):
    """生成历年体检指标数据（2022-2025），用于趋势可视化。"""
    from models.health_record import HealthRecord

    base_data = {
        member_ids[0]: {
            "白细胞计数": [6.2, 6.8, 7.1, 6.5],
            "红细胞计数": [4.5, 4.3, 4.6, 4.4],
            "血红蛋白": [142, 138, 145, 140],
            "血小板计数": [210, 225, 198, 240],
            "空腹血糖": [5.8, 6.2, 6.5, 6.8],
            "总胆固醇": [5.0, 5.3, 5.6, 5.8],
            "甘油三酯": [1.5, 1.8, 2.1, 2.3],
            "尿酸": [380, 410, 440, 460],
            "收缩压": [128, 135, 142, 138],
            "舒张压": [85, 88, 92, 86],
        },
        member_ids[1]: {
            "白细胞计数": [5.8, 6.0, 5.5, 5.9],
            "红细胞计数": [4.0, 3.9, 4.1, 3.8],
            "血红蛋白": [118, 112, 115, 108],
            "血小板计数": [180, 195, 170, 185],
            "空腹血糖": [6.1, 6.8, 7.2, 7.5],
            "总胆固醇": [4.8, 5.0, 5.2, 5.5],
            "甘油三酯": [1.6, 1.9, 2.0, 2.2],
            "尿酸": [290, 310, 305, 320],
        },
        member_ids[2]: {
            "白细胞计数": [6.5, 6.8, 6.0, 6.3],
            "红细胞计数": [5.0, 4.9, 5.1, 5.0],
            "血红蛋白": [155, 150, 152, 148],
            "血小板计数": [230, 245, 220, 235],
            "空腹血糖": [5.0, 5.2, 4.9, 5.1],
            "总胆固醇": [4.2, 4.5, 4.3, 4.6],
            "甘油三酯": [0.9, 1.2, 1.0, 1.1],
            "丙氨酸氨基转移酶": [25, 28, 32, 30],
        },
        member_ids[3]: {
            "白细胞计数": [5.5, 5.8, 6.0, 5.6],
            "红细胞计数": [4.2, 4.0, 4.1, 4.3],
            "血红蛋白": [120, 118, 125, 122],
            "血小板计数": [200, 210, 195, 215],
            "空腹血糖": [4.8, 5.0, 5.1, 4.9],
            "总胆固醇": [4.0, 4.2, 4.1, 4.3],
            "甘油三酯": [0.8, 0.9, 1.0, 0.7],
        },
    }

    from config import NORMAL_RANGES, INDICATOR_CATEGORIES
    indicator_to_category = {}
    for cat, indicators in INDICATOR_CATEGORIES.items():
        for ind in indicators:
            indicator_to_category[ind] = cat

    years = ["2022-05-10", "2023-05-12", "2024-05-08", "2025-05-15"]
    for mid, indicators in base_data.items():
        for ind_name, values in indicators.items():
            for i, val in enumerate(values):
                rng = NORMAL_RANGES.get(ind_name, ("", "", ""))
                ref = f"{rng[0]}~{rng[1]} {rng[2]}" if rng[0] != "" else ""
                record = HealthRecord(
                    member_id=mid,
                    record_date=years[i],
                    category=indicator_to_category.get(ind_name, "其他"),
                    indicator_name=ind_name,
                    indicator_value=str(val),
                    unit=rng[2] if rng[2] else "",
                    reference_range=ref,
                )
                record.save()


def _seed_medications(member_ids):
    from models.medication import Medication
    meds = [
        (member_ids[0], "氨氯地平片", "5mg", "每日一次", "2024-01-15", "", "降压药"),
        (member_ids[0], "非布司他片", "40mg", "每日一次", "2024-06-01", "", "降尿酸"),
        (member_ids[1], "二甲双胍缓释片", "0.5g", "每日两次", "2024-03-20", "", "降糖药"),
        (member_ids[2], "维生素B族", "1片", "每日一次", "2025-01-10", "", "营养补充"),
    ]
    for mid, name, dose, freq, start, end, note in meds:
        Medication(
            member_id=mid, drug_name=name, dosage=dose, frequency=freq,
            start_date=start, end_date=end, note=note,
        ).save()


def _seed_reminders(member_ids):
    from models.reminder import Reminder
    now = datetime.now()
    reminders = [
        (member_ids[0], "心内科复诊", "请携带上次心电图报告", "复诊",
         (now + timedelta(days=3)).strftime("%Y-%m-%d %H:%M"), "once"),
        (member_ids[0], "服用降压药", "氨氯地平片 5mg，饭后服用", "服药",
         (now + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M"), "daily"),
        (member_ids[1], "测空腹血糖", "晨起测量并记录血糖值", "检查",
         (now + timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), "daily"),
        (member_ids[1], "内分泌科复诊", "复查糖化血红蛋白", "复诊",
         (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M"), "once"),
        (member_ids[2], "年度体检", "预约公司年度健康体检", "检查",
         (now + timedelta(days=15)).strftime("%Y-%m-%d %H:%M"), "once"),
        (member_ids[3], "服用维生素B", "饭后服用", "服药",
         (now + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M"), "daily"),
    ]
    for mid, title, content, rtype, rtime, repeat in reminders:
        Reminder(
            member_id=mid, title=title, content=content,
            remind_type=rtype, remind_time=rtime, repeat_rule=repeat,
        ).save()


def _seed_medical_history(member_ids):
    from models.medical_history import MedicalHistory
    histories = [
        (member_ids[0], "高血压", "2018-03-01", "市人民医院", "控制中", "高血压2级"),
        (member_ids[0], "痛风", "2020-06-15", "市人民医院", "控制中", "高尿酸血症"),
        (member_ids[1], "2型糖尿病", "2019-09-20", "省中医院", "控制中", "空腹血糖偏高"),
        (member_ids[2], "脂肪肝", "2023-08-10", "体检中心", "已恢复", "轻度脂肪肝"),
    ]
    for mid, disease, date, hospital, status, desc in histories:
        MedicalHistory(
            member_id=mid, disease_name=disease, diagnose_date=date,
            hospital=hospital, status=status, description=desc,
        ).save()
