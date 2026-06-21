"""
颐康管家 - 档案中心视图
左侧树形控件展示家族成员关系，右侧展示选中成员的完整病史、
体检记录、用药记录等，支持新增、编辑、删除操作。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QFormLayout, QSplitter, QMessageBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal

from controllers.member_controller import MemberController
from controllers.record_controller import RecordController
from controllers.reminder_controller import ReminderController
from controllers.misc_controller import MedicationController, HistoryController
from views.dialogs import (
    MemberDialog, RecordDialog, ReminderDialog, MedicationDialog, HistoryDialog
)


class ArchiveView(QWidget):
    """档案中心视图。"""

    member_selected = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._member_ctrl = MemberController()
        self._record_ctrl = RecordController()
        self._reminder_ctrl = ReminderController()
        self._med_ctrl = MedicationController()
        self._hist_ctrl = HistoryController()
        self._current_member_id = None
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        left_panel = QGroupBox("家庭成员")
        left_panel.setObjectName("CardBox")
        left_panel.setFixedWidth(260)
        left_layout = QVBoxLayout(left_panel)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_tree_clicked)
        left_layout.addWidget(self.tree)

        btn_layout = QHBoxLayout()
        self.add_member_btn = QPushButton("新增")
        self.add_member_btn.setObjectName("PrimaryButton")
        self.add_member_btn.clicked.connect(self._add_member)
        self.del_member_btn = QPushButton("删除")
        self.del_member_btn.setObjectName("DangerButton")
        self.del_member_btn.clicked.connect(self._del_member)
        btn_layout.addWidget(self.add_member_btn)
        btn_layout.addWidget(self.del_member_btn)
        left_layout.addLayout(btn_layout)
        main_layout.addWidget(left_panel)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.info_group = QGroupBox("成员信息")
        self.info_group.setObjectName("CardBox")
        info_layout = QFormLayout(self.info_group)
        self.info_labels = {}
        for field in ["姓名", "性别", "出生日期", "家庭关系", "血型", "联系电话", "过敏史", "备注"]:
            label = QLabel("—")
            self.info_labels[field] = label
            info_layout.addRow(f"{field}：", label)
        right_layout.addWidget(self.info_group)

        self.tabs = QTabWidget()
        self._build_records_tab()
        self._build_medication_tab()
        self._build_history_tab()
        self._build_reminders_tab()
        right_layout.addWidget(self.tabs, 1)
        main_layout.addWidget(right_panel, 1)

        self.info_group.setEnabled(False)
        self.tabs.setEnabled(False)

    def _build_records_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        btn_layout = QHBoxLayout()
        self.add_record_btn = QPushButton("新增记录")
        self.add_record_btn.setObjectName("PrimaryButton")
        self.add_record_btn.clicked.connect(self._add_record)
        self.import_ocr_btn = QPushButton("OCR导入")
        self.import_ocr_btn.clicked.connect(self._import_ocr)
        self.del_record_btn = QPushButton("删除")
        self.del_record_btn.clicked.connect(self._del_record)
        btn_layout.addWidget(self.add_record_btn)
        btn_layout.addWidget(self.import_ocr_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.del_record_btn)
        layout.addLayout(btn_layout)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(6)
        self.record_table.setHorizontalHeaderLabels(
            ["日期", "类别", "指标", "数值", "参考范围", "状态"]
        )
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.record_table.setAlternatingRowColors(True)
        self.record_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.record_table)
        self.tabs.addTab(tab, "体检记录")

    def _build_medication_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        btn_layout = QHBoxLayout()
        self.add_med_btn = QPushButton("新增用药")
        self.add_med_btn.setObjectName("PrimaryButton")
        self.add_med_btn.clicked.connect(self._add_medication)
        self.del_med_btn = QPushButton("删除")
        self.del_med_btn.clicked.connect(self._del_medication)
        btn_layout.addWidget(self.add_med_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.del_med_btn)
        layout.addLayout(btn_layout)

        self.med_table = QTableWidget()
        self.med_table.setColumnCount(5)
        self.med_table.setHorizontalHeaderLabels(
            ["药品", "剂量", "频率", "起止日期", "备注"]
        )
        self.med_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.med_table.setAlternatingRowColors(True)
        self.med_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.med_table)
        self.tabs.addTab(tab, "用药记录")

    def _build_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        btn_layout = QHBoxLayout()
        self.add_hist_btn = QPushButton("新增病史")
        self.add_hist_btn.setObjectName("PrimaryButton")
        self.add_hist_btn.clicked.connect(self._add_history)
        self.del_hist_btn = QPushButton("删除")
        self.del_hist_btn.clicked.connect(self._del_history)
        btn_layout.addWidget(self.add_hist_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.del_hist_btn)
        layout.addLayout(btn_layout)

        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(5)
        self.hist_table.setHorizontalHeaderLabels(
            ["疾病", "确诊日期", "医院", "状态", "描述"]
        )
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hist_table.setAlternatingRowColors(True)
        self.hist_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.hist_table)
        self.tabs.addTab(tab, "病史记录")

    def _build_reminders_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        btn_layout = QHBoxLayout()
        self.add_rem_btn = QPushButton("新增提醒")
        self.add_rem_btn.setObjectName("PrimaryButton")
        self.add_rem_btn.clicked.connect(self._add_reminder)
        self.done_rem_btn = QPushButton("标记完成")
        self.done_rem_btn.clicked.connect(self._mark_reminder_done)
        self.del_rem_btn = QPushButton("删除")
        self.del_rem_btn.clicked.connect(self._del_reminder)
        btn_layout.addWidget(self.add_rem_btn)
        btn_layout.addWidget(self.done_rem_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.del_rem_btn)
        layout.addLayout(btn_layout)

        self.rem_table = QTableWidget()
        self.rem_table.setColumnCount(5)
        self.rem_table.setHorizontalHeaderLabels(
            ["标题", "类型", "时间", "重复", "状态"]
        )
        self.rem_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rem_table.setAlternatingRowColors(True)
        self.rem_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.rem_table)
        self.tabs.addTab(tab, "提醒事项")

    def refresh(self, member_id=None):
        self._load_tree()
        if member_id:
            self._select_member(member_id)
        elif self._current_member_id:
            self._load_member_details(self._current_member_id)

    def _load_tree(self):
        self.tree.clear()
        roots = self._member_ctrl.build_family_tree()
        for root in roots:
            self._add_tree_node(self.tree, root)

    def _add_tree_node(self, parent, member):
        text = f"{member.name}（{member.relation}）"
        node = QTreeWidgetItem(parent, [text])
        node.setData(0, Qt.UserRole, member.id)
        node.setIcon(0, _gender_icon(member.gender))
        for child in getattr(member, "_tree_children", []):
            self._add_tree_node(node, child)
            node.setExpanded(True)
        return node

    def _on_tree_clicked(self, item, column):
        member_id = item.data(0, Qt.UserRole)
        if member_id:
            self._select_member(member_id)

    def _select_member(self, member_id):
        self._current_member_id = member_id
        self.info_group.setEnabled(True)
        self.tabs.setEnabled(True)
        self._load_member_details(member_id)
        self.member_selected.emit(member_id)

    def _load_member_details(self, member_id):
        member = self._member_ctrl.get_member(member_id)
        if not member:
            return
        self.info_labels["姓名"].setText(member.name)
        self.info_labels["性别"].setText(member.gender)
        self.info_labels["出生日期"].setText(
            f"{member.birth_date}（{member.age()}岁）")
        self.info_labels["家庭关系"].setText(member.relation)
        self.info_labels["血型"].setText(member.blood_type or "未填写")
        self.info_labels["联系电话"].setText(member.phone or "未填写")
        self.info_labels["过敏史"].setText(member.allergy or "无")
        self.info_labels["备注"].setText(member.note or "无")
        self._load_records(member_id)
        self._load_medications(member_id)
        self._load_history(member_id)
        self._load_reminders(member_id)

    def _load_records(self, member_id):
        records = self._record_ctrl.get_records_by_member(member_id)
        records.sort(key=lambda r: r.record_date, reverse=True)
        self.record_table.setRowCount(len(records))
        for i, r in enumerate(records):
            self.record_table.setItem(i, 0, QTableWidgetItem(r.record_date))
            self.record_table.setItem(i, 1, QTableWidgetItem(r.category))
            self.record_table.setItem(i, 2, QTableWidgetItem(r.indicator_name))
            val_item = QTableWidgetItem(f"{r.indicator_value} {r.unit}".strip())
            if r.is_abnormal:
                val_item.setForeground(Qt.red)
            self.record_table.setItem(i, 3, val_item)
            self.record_table.setItem(i, 4, QTableWidgetItem(r.reference_range))
            status = "⚠异常" if r.is_abnormal else "正常"
            self.record_table.setItem(i, 5, QTableWidgetItem(status))

    def _load_medications(self, member_id):
        meds = self._med_ctrl.get_by_member(member_id)
        self.med_table.setRowCount(len(meds))
        for i, m in enumerate(meds):
            self.med_table.setItem(i, 0, QTableWidgetItem(m.drug_name))
            self.med_table.setItem(i, 1, QTableWidgetItem(m.dosage))
            self.med_table.setItem(i, 2, QTableWidgetItem(m.frequency))
            period = m.start_date or ""
            if m.end_date:
                period += f" ~ {m.end_date}"
            elif m.start_date:
                period += " ~ 长期"
            self.med_table.setItem(i, 3, QTableWidgetItem(period))
            self.med_table.setItem(i, 4, QTableWidgetItem(m.note))

    def _load_history(self, member_id):
        hists = self._hist_ctrl.get_by_member(member_id)
        self.hist_table.setRowCount(len(hists))
        for i, h in enumerate(hists):
            self.hist_table.setItem(i, 0, QTableWidgetItem(h.disease_name))
            self.hist_table.setItem(i, 1, QTableWidgetItem(h.diagnose_date))
            self.hist_table.setItem(i, 2, QTableWidgetItem(h.hospital))
            self.hist_table.setItem(i, 3, QTableWidgetItem(h.status))
            self.hist_table.setItem(i, 4, QTableWidgetItem(h.description))

    def _load_reminders(self, member_id):
        rems = self._reminder_ctrl.get_reminders_by_member(member_id)
        self.rem_table.setRowCount(len(rems))
        for i, r in enumerate(rems):
            self.rem_table.setItem(i, 0, QTableWidgetItem(r.title))
            self.rem_table.setItem(i, 1, QTableWidgetItem(r.remind_type))
            self.rem_table.setItem(i, 2, QTableWidgetItem(r.remind_time))
            repeat = {"once": "仅一次", "daily": "每日"}.get(r.repeat_rule, r.repeat_rule)
            self.rem_table.setItem(i, 3, QTableWidgetItem(repeat))
            status = "已完成" if r.is_done else "待办"
            self.rem_table.setItem(i, 4, QTableWidgetItem(status))

    def _add_member(self):
        parents = self._member_ctrl.get_all_members()
        dlg = MemberDialog(self, member=None, parent_members=parents)
        if dlg.exec():
            data = dlg.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "提示", "请输入姓名")
                return
            self._member_ctrl.save_member(data)
            self.refresh()

    def _del_member(self):
        if not self._current_member_id:
            return
        reply = QMessageBox.question(
            self, "确认删除",
            "删除成员将同时删除其所有健康记录，确定删除吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._member_ctrl.delete_member(self._current_member_id)
            self._current_member_id = None
            self.info_group.setEnabled(False)
            self.tabs.setEnabled(False)
            self.refresh()

    def _add_record(self):
        if not self._current_member_id:
            return
        dlg = RecordDialog(self, member_id=self._current_member_id)
        if dlg.exec():
            data = dlg.get_data()
            self._record_ctrl.save_record(data)
            self._load_records(self._current_member_id)

    def _import_ocr(self):
        if not self._current_member_id:
            return
        from views.dialogs import OCRImportDialog
        dlg = OCRImportDialog(self, member_id=self._current_member_id)
        if dlg.exec():
            self._load_records(self._current_member_id)

    def _del_record(self):
        row = self.record_table.currentRow()
        if row < 0:
            return
        date_str = self.record_table.item(row, 0).text()
        ind_name = self.record_table.item(row, 2).text()
        records = self._record_ctrl.get_records_by_member(self._current_member_id)
        for r in records:
            if r.record_date == date_str and r.indicator_name == ind_name:
                self._record_ctrl.delete_record(r.id)
                break
        self._load_records(self._current_member_id)

    def _add_medication(self):
        if not self._current_member_id:
            return
        dlg = MedicationDialog(self, member_id=self._current_member_id)
        if dlg.exec():
            self._med_ctrl.save(dlg.get_data())
            self._load_medications(self._current_member_id)

    def _del_medication(self):
        row = self.med_table.currentRow()
        if row < 0:
            return
        meds = self._med_ctrl.get_by_member(self._current_member_id)
        if row < len(meds):
            self._med_ctrl.delete(meds[row].id)
            self._load_medications(self._current_member_id)

    def _add_history(self):
        if not self._current_member_id:
            return
        dlg = HistoryDialog(self, member_id=self._current_member_id)
        if dlg.exec():
            self._hist_ctrl.save(dlg.get_data())
            self._load_history(self._current_member_id)

    def _del_history(self):
        row = self.hist_table.currentRow()
        if row < 0:
            return
        hists = self._hist_ctrl.get_by_member(self._current_member_id)
        if row < len(hists):
            self._hist_ctrl.delete(hists[row].id)
            self._load_history(self._current_member_id)

    def _add_reminder(self):
        if not self._current_member_id:
            return
        dlg = ReminderDialog(self, member_id=self._current_member_id)
        if dlg.exec():
            self._reminder_ctrl.save_reminder(dlg.get_data())
            self._load_reminders(self._current_member_id)

    def _mark_reminder_done(self):
        row = self.rem_table.currentRow()
        if row < 0:
            return
        rems = self._reminder_ctrl.get_reminders_by_member(self._current_member_id)
        if row < len(rems):
            self._reminder_ctrl.mark_done(rems[row].id)
            self._load_reminders(self._current_member_id)

    def _del_reminder(self):
        row = self.rem_table.currentRow()
        if row < 0:
            return
        rems = self._reminder_ctrl.get_reminders_by_member(self._current_member_id)
        if row < len(rems):
            self._reminder_ctrl.delete_reminder(rems[row].id)
            self._load_reminders(self._current_member_id)


def _gender_icon(gender):
    from PySide6.QtGui import QIcon
    return QIcon()
