"""
颐康管家 - 对话框模块
提供家庭成员、体检记录、提醒事项的新增/编辑对话框，以及OCR导入流程对话框。
"""
from datetime import date

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QSpinBox, QDateEdit, QDateTimeEdit, QTextEdit, QPushButton, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QCheckBox, QFileDialog, QProgressBar, QWidget, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDateTime, Signal

from config import INDICATOR_CATEGORIES, NORMAL_RANGES
from controllers.ocr_controller import OCRController


DIALOG_STYLE = """
QDialog {
    background-color: #ffffff;
}
QLabel {
    color: #2c3e50;
    font-size: 13px;
}
QPushButton {
    color: #2c3e50;
}
QPushButton#PrimaryButton {
    background-color: #2980b9;
    color: #ffffff;
    border: 1px solid #21618c;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
    font-weight: bold;
    min-width: 80px;
}
QPushButton#PrimaryButton:hover { background-color: #21618c; }
QPushButton#PrimaryButton:pressed { background-color: #1a5276; }
QPushButton#DangerButton {
    background-color: #c0392b;
    color: #ffffff;
    border: 1px solid #922b21;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton#DangerButton:hover { background-color: #922b21; }
"""


class MemberDialog(QDialog):
    """家庭成员新增/编辑对话框。"""

    def __init__(self, parent=None, member=None, parent_members=None):
        super().__init__(parent)
        self.member = member
        self.setWindowTitle("编辑成员" if member else "新增成员")
        self.setMinimumWidth(420)
        self.setStyleSheet(DIALOG_STYLE)
        self._setup_ui(parent_members)

    def _setup_ui(self, parent_members):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(self.member.name if self.member else "")
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        if self.member and self.member.gender:
            self.gender_combo.setCurrentText(self.member.gender)
        self.birth_edit = QDateEdit()
        self.birth_edit.setDisplayFormat("yyyy-MM-dd")
        self.birth_edit.setCalendarPopup(True)
        if self.member and self.member.birth_date:
            self.birth_edit.setDate(QDateTime.fromString(
                self.member.birth_date, "yyyy-MM-dd").date())
        else:
            self.birth_edit.setDate(date(1990, 1, 1))
        self.id_card_edit = QLineEdit(self.member.id_card if self.member else "")
        self.phone_edit = QLineEdit(self.member.phone if self.member else "")
        self.relation_edit = QLineEdit(self.member.relation if self.member else "")
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("无（根成员）", None)
        if parent_members:
            for pm in parent_members:
                if self.member and pm.id == self.member.id:
                    continue
                self.parent_combo.addItem(f"{pm.name} ({pm.relation})", pm.id)
        if self.member and self.member.parent_id:
            idx = self.parent_combo.findData(self.member.parent_id)
            if idx >= 0:
                self.parent_combo.setCurrentIndex(idx)
        self.blood_combo = QComboBox()
        self.blood_combo.addItems(["", "A型", "B型", "AB型", "O型"])
        if self.member and self.member.blood_type:
            self.blood_combo.setCurrentText(self.member.blood_type)
        self.allergy_edit = QLineEdit(self.member.allergy if self.member else "")
        self.note_edit = QTextEdit(self.member.note if self.member else "")
        self.note_edit.setMaximumHeight(60)

        layout.addRow("姓名：", self.name_edit)
        layout.addRow("性别：", self.gender_combo)
        layout.addRow("出生日期：", self.birth_edit)
        layout.addRow("身份证号：", self.id_card_edit)
        layout.addRow("联系电话：", self.phone_edit)
        layout.addRow("家庭关系：", self.relation_edit)
        layout.addRow("父/母节点：", self.parent_combo)
        layout.addRow("血型：", self.blood_combo)
        layout.addRow("过敏史：", self.allergy_edit)
        layout.addRow("备注：", self.note_edit)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_container)

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "gender": self.gender_combo.currentText(),
            "birth_date": self.birth_edit.date().toString("yyyy-MM-dd"),
            "id_card": self.id_card_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "relation": self.relation_edit.text().strip(),
            "parent_id": self.parent_combo.currentData(),
            "blood_type": self.blood_combo.currentText(),
            "allergy": self.allergy_edit.text().strip(),
            "note": self.note_edit.toPlainText().strip(),
            "id": self.member.id if self.member else None,
        }


class RecordDialog(QDialog):
    """体检记录新增/编辑对话框。"""

    def __init__(self, parent=None, record=None, member_id=None):
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("编辑记录" if record else "新增体检记录")
        self.setMinimumWidth(450)
        self.setStyleSheet(DIALOG_STYLE)
        self._member_id = member_id or (record.member_id if record else None)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        if self.record and self.record.record_date:
            self.date_edit.setDate(QDateTime.fromString(
                self.record.record_date, "yyyy-MM-dd").date())
        else:
            self.date_edit.setDate(date.today())

        self.category_combo = QComboBox()
        cats = list(INDICATOR_CATEGORIES.keys()) + ["其他"]
        self.category_combo.addItems(cats)
        self.category_combo.currentTextChanged.connect(self._on_category_changed)
        if self.record and self.record.category:
            self.category_combo.setCurrentText(self.record.category)

        self.indicator_combo = QComboBox()
        all_inds = []
        for inds in INDICATOR_CATEGORIES.values():
            all_inds.extend(inds)
        all_inds = list(dict.fromkeys(all_inds))
        self.indicator_combo.addItems(all_inds)
        self.indicator_combo.setEditable(True)
        if self.record and self.record.indicator_name:
            self.indicator_combo.setCurrentText(self.record.indicator_name)
        self.indicator_combo.currentTextChanged.connect(self._on_indicator_changed)

        self.value_edit = QLineEdit(self.record.indicator_value if self.record else "")
        self.unit_edit = QLineEdit(self.record.unit if self.record else "")
        self.ref_edit = QLineEdit(self.record.reference_range if self.record else "")

        self.note_edit = QTextEdit(self.record.note if self.record else "")
        self.note_edit.setMaximumHeight(60)

        layout.addRow("记录日期：", self.date_edit)
        layout.addRow("检查类别：", self.category_combo)
        layout.addRow("指标名称：", self.indicator_combo)
        layout.addRow("指标数值：", self.value_edit)
        layout.addRow("单位：", self.unit_edit)
        layout.addRow("参考范围：", self.ref_edit)
        layout.addRow("备注：", self.note_edit)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_container)

        self._on_indicator_changed()

    def _on_category_changed(self):
        cat = self.category_combo.currentText()
        inds = INDICATOR_CATEGORIES.get(cat, [])
        self.indicator_combo.clear()
        self.indicator_combo.addItems(inds)

    def _on_indicator_changed(self):
        name = self.indicator_combo.currentText()
        rng = NORMAL_RANGES.get(name)
        if rng and rng[0] != "":
            self.unit_edit.setText(rng[2])
            self.ref_edit.setText(f"{rng[0]}~{rng[1]} {rng[2]}")
        elif rng:
            self.unit_edit.setText(rng[2])

    def get_data(self):
        return {
            "member_id": self._member_id,
            "record_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "category": self.category_combo.currentText(),
            "indicator_name": self.indicator_combo.currentText().strip(),
            "indicator_value": self.value_edit.text().strip(),
            "unit": self.unit_edit.text().strip(),
            "reference_range": self.ref_edit.text().strip(),
            "note": self.note_edit.toPlainText().strip(),
            "id": self.record.id if self.record else None,
        }


class ReminderDialog(QDialog):
    """提醒事项新增/编辑对话框。"""

    def __init__(self, parent=None, reminder=None, member_id=None):
        super().__init__(parent)
        self.reminder = reminder
        self.setWindowTitle("编辑提醒" if reminder else "新增提醒")
        self.setMinimumWidth(400)
        self.setStyleSheet(DIALOG_STYLE)
        self._member_id = member_id or (reminder.member_id if reminder else None)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)

        self.title_edit = QLineEdit(self.reminder.title if self.reminder else "")
        self.type_combo = QComboBox()
        self.type_combo.addItems(["复诊", "服药", "检查", "其他"])
        if self.reminder and self.reminder.remind_type:
            self.type_combo.setCurrentText(self.reminder.remind_type)

        self.time_edit = QDateTimeEdit()
        self.time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.time_edit.setCalendarPopup(True)
        if self.reminder and self.reminder.remind_time:
            self.time_edit.setDateTime(QDateTime.fromString(
                self.reminder.remind_time, "yyyy-MM-dd HH:mm"))
        else:
            self.time_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        self.repeat_combo = QComboBox()
        self.repeat_combo.addItems(["once", "daily"])
        self.repeat_combo.setItemData(0, "仅一次")
        self.repeat_combo.setItemData(1, "每日重复")
        if self.reminder and self.reminder.repeat_rule:
            idx = self.repeat_combo.findText(self.reminder.repeat_rule)
            if idx >= 0:
                self.repeat_combo.setCurrentIndex(idx)

        self.content_edit = QTextEdit(self.reminder.content if self.reminder else "")
        self.content_edit.setMaximumHeight(80)

        layout.addRow("标题：", self.title_edit)
        layout.addRow("提醒类型：", self.type_combo)
        layout.addRow("提醒时间：", self.time_edit)
        layout.addRow("重复规则：", self.repeat_combo)
        layout.addRow("内容：", self.content_edit)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_container)

    def get_data(self):
        return {
            "member_id": self._member_id,
            "title": self.title_edit.text().strip(),
            "remind_type": self.type_combo.currentText(),
            "remind_time": self.time_edit.dateTime().toString("yyyy-MM-dd HH:mm"),
            "repeat_rule": self.repeat_combo.currentText(),
            "content": self.content_edit.toPlainText().strip(),
            "id": self.reminder.id if self.reminder else None,
        }


class MedicationDialog(QDialog):
    """用药记录新增/编辑对话框。"""

    def __init__(self, parent=None, med=None, member_id=None):
        super().__init__(parent)
        self.med = med
        self.setWindowTitle("编辑用药" if med else "新增用药")
        self.setMinimumWidth(400)
        self.setStyleSheet(DIALOG_STYLE)
        self._member_id = member_id or (med.member_id if med else None)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        self.drug_edit = QLineEdit(self.med.drug_name if self.med else "")
        self.dosage_edit = QLineEdit(self.med.dosage if self.med else "")
        self.freq_edit = QLineEdit(self.med.frequency if self.med else "")

        self.start_edit = QDateEdit()
        self.start_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_edit.setCalendarPopup(True)
        if self.med and self.med.start_date:
            self.start_edit.setDate(QDateTime.fromString(
                self.med.start_date, "yyyy-MM-dd").date())
        else:
            self.start_edit.setDate(date.today())

        self.end_edit = QDateEdit()
        self.end_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setSpecialValueText("长期")
        if self.med and self.med.end_date:
            self.end_edit.setDate(QDateTime.fromString(
                self.med.end_date, "yyyy-MM-dd").date())
        else:
            self.end_edit.setDate(self.end_edit.minimumDate())

        self.note_edit = QLineEdit(self.med.note if self.med else "")

        layout.addRow("药品名称：", self.drug_edit)
        layout.addRow("剂量：", self.dosage_edit)
        layout.addRow("用药频率：", self.freq_edit)
        layout.addRow("开始日期：", self.start_edit)
        layout.addRow("结束日期：", self.end_edit)
        layout.addRow("备注：", self.note_edit)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_container)

    def get_data(self):
        return {
            "member_id": self._member_id,
            "drug_name": self.drug_edit.text().strip(),
            "dosage": self.dosage_edit.text().strip(),
            "frequency": self.freq_edit.text().strip(),
            "start_date": self.start_edit.date().toString("yyyy-MM-dd"),
            "end_date": self.end_edit.date().toString("yyyy-MM-dd")
            if self.end_edit.date() != self.end_edit.minimumDate() else "",
            "note": self.note_edit.text().strip(),
            "id": self.med.id if self.med else None,
        }


class HistoryDialog(QDialog):
    """病史记录新增/编辑对话框。"""

    def __init__(self, parent=None, history=None, member_id=None):
        super().__init__(parent)
        self.history = history
        self.setWindowTitle("编辑病史" if history else "新增病史")
        self.setMinimumWidth(420)
        self.setStyleSheet(DIALOG_STYLE)
        self._member_id = member_id or (history.member_id if history else None)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        self.disease_edit = QLineEdit(self.history.disease_name if self.history else "")
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        if self.history and self.history.diagnose_date:
            self.date_edit.setDate(QDateTime.fromString(
                self.history.diagnose_date, "yyyy-MM-dd").date())
        else:
            self.date_edit.setDate(date.today())
        self.hospital_edit = QLineEdit(self.history.hospital if self.history else "")
        self.status_combo = QComboBox()
        self.status_combo.addItems(["治疗中", "已恢复", "观察中", "已痊愈"])
        if self.history and self.history.status:
            self.status_combo.setCurrentText(self.history.status)
        self.desc_edit = QTextEdit(self.history.description if self.history else "")
        self.desc_edit.setMaximumHeight(80)

        layout.addRow("疾病名称：", self.disease_edit)
        layout.addRow("确诊日期：", self.date_edit)
        layout.addRow("就诊医院：", self.hospital_edit)
        layout.addRow("当前状态：", self.status_combo)
        layout.addRow("病情描述：", self.desc_edit)

        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setMinimumWidth(100)
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_container)

    def get_data(self):
        return {
            "member_id": self._member_id,
            "disease_name": self.disease_edit.text().strip(),
            "diagnose_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "hospital": self.hospital_edit.text().strip(),
            "status": self.status_combo.currentText(),
            "description": self.desc_edit.toPlainText().strip(),
            "id": self.history.id if self.history else None,
        }


class OCRImportDialog(QDialog):
    """OCR 智能识别导入对话框。"""

    def __init__(self, parent=None, member_id=None):
        super().__init__(parent)
        self.setWindowTitle("OCR 智能识别 - 导入体检报告")
        self.setMinimumWidth(600)
        self.setStyleSheet(DIALOG_STYLE)
        self._member_id = member_id
        self._ocr = OCRController()
        self._file_path = None
        self._structured = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        info_label = QLabel("拖入或选择体检报告图片/PDF文件，系统将自动识别关键字段。")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        file_layout = QHBoxLayout()
        self.file_btn = QPushButton("选择文件...")
        self.file_btn.clicked.connect(self._select_file)
        self.file_label = QLabel("未选择文件")
        self.file_label.setStyleSheet("color: #7f8c8d;")
        file_layout.addWidget(self.file_btn)
        file_layout.addWidget(self.file_label, 1)
        layout.addLayout(file_layout)

        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("报告日期："))
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(date.today())
        date_layout.addWidget(self.date_edit)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        self.recognize_btn = QPushButton("开始识别")
        self.recognize_btn.setObjectName("PrimaryButton")
        self.recognize_btn.clicked.connect(self._recognize)
        layout.addWidget(self.recognize_btn)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        self.result_group = QGroupBox("识别结果（可编辑）")
        result_layout = QVBoxLayout(self.result_group)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["指标名称", "数值", "单位", "参考范围", "异常"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        result_layout.addWidget(self.table)
        self.result_group.setVisible(False)
        layout.addWidget(self.result_group)

        self.raw_text = QTextEdit()
        self.raw_text.setPlaceholderText("识别原始文本...")
        self.raw_text.setMaximumHeight(120)
        self.raw_text.setVisible(False)
        layout.addWidget(self.raw_text)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存到数据库")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self._save_records)
        self.save_btn.setEnabled(False)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择体检报告",
            "", "图片文件 (*.png *.jpg *.jpeg *.bmp *.tiff);;PDF文件 (*.pdf);;所有文件 (*)"
        )
        if path:
            self._file_path = path
            self.file_label.setText(path)
            self.file_label.setStyleSheet("color: #27ae60;")

    def _recognize(self):
        if not self._file_path:
            QMessageBox.warning(self, "提示", "请先选择文件")
            return
        if not self._ocr.is_ocr_available():
            QMessageBox.warning(self, "OCR不可用", "Tesseract 引擎未安装，无法进行OCR识别。")
            return
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)
        self.recognize_btn.setEnabled(False)
        import time
        start = time.time()
        result = self._ocr.recognize_report(self._file_path)
        elapsed = time.time() - start
        self.progress.setVisible(False)
        self.recognize_btn.setEnabled(True)

        if result.get("success"):
            self._structured = result.get("structured", [])
            self._populate_table(self._structured)
            self.raw_text.setPlainText(result.get("raw_text", ""))
            self.raw_text.setVisible(True)
            self.result_group.setVisible(True)
            self.save_btn.setEnabled(True)
            QMessageBox.information(
                self, "识别完成",
                result.get("message", "") + f"\n耗时 {elapsed:.1f}s"
            )
        else:
            QMessageBox.warning(self, "识别失败", result.get("message", "未知错误"))

    def _populate_table(self, items):
        self.table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(item["indicator_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(item["indicator_value"]))
            self.table.setItem(i, 2, QTableWidgetItem(item["unit"]))
            self.table.setItem(i, 3, QTableWidgetItem(item["reference_range"]))
            abnormal_item = QTableWidgetItem("⚠ 异常" if item["is_abnormal"] else "正常")
            abnormal_item.setFlags(Qt.ItemIsEnabled)
            self.table.setItem(i, 4, abnormal_item)

    def _get_edited_data(self):
        items = []
        for i in range(self.table.rowCount()):
            name = self.table.item(i, 0).text().strip()
            value = self.table.item(i, 1).text().strip()
            if not name or not value:
                continue
            items.append({
                "indicator_name": name,
                "indicator_value": value,
                "unit": self.table.item(i, 2).text().strip(),
                "category": "其他",
            })
        return items

    def _save_records(self):
        if not self._member_id:
            QMessageBox.warning(self, "提示", "请先选择家庭成员")
            return
        edited = self._get_edited_data()
        if not edited:
            QMessageBox.warning(self, "提示", "没有可保存的指标数据")
            return
        report_date = self.date_edit.date().toString("yyyy-MM-dd")
        report_path = self._ocr.import_file(self._file_path)
        saved = self._ocr.save_recognized_records(
            self._member_id, edited, report_date, report_path
        )
        QMessageBox.information(self, "保存成功", f"已保存 {len(saved)} 条体检记录")
        self.accept()
