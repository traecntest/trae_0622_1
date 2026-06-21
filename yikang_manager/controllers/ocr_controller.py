"""
颐康管家 - OCR 识别控制器
协调体检报告图片/PDF的导入、OCR识别与结构化数据入库。
"""
import os
import shutil

from utils.ocr_engine import ocr_engine
from config import REPORT_DIR, NORMAL_RANGES


class OCRController:
    """OCR 识别控制器。"""

    def is_ocr_available(self):
        return ocr_engine.is_available()

    def import_file(self, src_path):
        """导入文件到报告目录，返回存储路径。"""
        if not os.path.exists(src_path):
            return None
        filename = os.path.basename(src_path)
        dest = os.path.join(REPORT_DIR, filename)
        shutil.copy2(src_path, dest)
        return dest

    def recognize_report(self, file_path):
        """识别体检报告，返回结构化结果。"""
        result = ocr_engine.recognize(file_path)
        if result.get("success"):
            result["structured"] = self._structure_indicators(result["indicators"])
        return result

    def _structure_indicators(self, indicators):
        """将识别到的指标转换为可入库的结构化列表。"""
        structured = []
        from config import INDICATOR_CATEGORIES
        ind_to_cat = {}
        for cat, inds in INDICATOR_CATEGORIES.items():
            for ind in inds:
                ind_to_cat[ind] = cat

        for name, info in indicators.items():
            value = info["value"]
            unit = info.get("unit", "") or NORMAL_RANGES.get(name, ("", "", ""))[2]
            rng = NORMAL_RANGES.get(name)
            ref = ""
            if rng and rng[0] != "":
                ref = f"{rng[0]}~{rng[1]} {rng[2]}"
            is_abnormal = 0
            if rng and rng[0] != "":
                try:
                    v = float(value)
                    is_abnormal = 1 if (v < rng[0] or v > rng[1]) else 0
                except (ValueError, TypeError):
                    pass
            structured.append({
                "indicator_name": name,
                "indicator_value": value,
                "unit": unit,
                "category": ind_to_cat.get(name, "其他"),
                "reference_range": ref,
                "is_abnormal": is_abnormal,
            })
        return structured

    def save_recognized_records(self, member_id, structured, report_date, report_path):
        """将识别到的指标批量保存到数据库。"""
        from models.health_record import HealthRecord
        saved = []
        for item in structured:
            record = HealthRecord(
                member_id=member_id,
                record_date=report_date or __import__("datetime").date.today().isoformat(),
                category=item["category"],
                indicator_name=item["indicator_name"],
                indicator_value=item["indicator_value"],
                unit=item["unit"],
                reference_range=item["reference_range"],
                report_image=report_path,
            )
            record.save()
            saved.append(record)
        return saved
