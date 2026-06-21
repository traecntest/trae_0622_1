"""
颐康管家 - 全局搜索视图
支持模糊搜索家庭成员、体检记录、病史等，输入疾病或时间关键字即可秒查。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox
)
from PySide6.QtCore import Qt, Signal

from controllers.member_controller import MemberController
from controllers.record_controller import RecordController
from controllers.misc_controller import HistoryController


class SearchView(QWidget):
    """全局搜索视图。"""

    member_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._member_ctrl = MemberController()
        self._record_ctrl = RecordController()
        self._hist_ctrl = HistoryController()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("全局搜索")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a5276;")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入疾病名称、指标名、日期、姓名等关键字...")
        self.search_edit.returnPressed.connect(self._search)
        self.search_edit.textChanged.connect(self._on_text_changed)
        search_layout.addWidget(self.search_edit, 1)
        self.search_btn = QPushButton("搜索")
        self.search_btn.setObjectName("PrimaryButton")
        self.search_btn.clicked.connect(self._search)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        self.hint_label = QLabel("提示：输入「高血压」「2024」「白细胞」等关键字进行搜索")
        self.hint_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(self.hint_label)

        self.tabs = QTabWidget()
        self._build_member_tab()
        self._build_record_tab()
        self._build_history_tab()
        layout.addWidget(self.tabs, 1)

    def _build_member_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.member_table = QTableWidget()
        self.member_table.setColumnCount(5)
        self.member_table.setHorizontalHeaderLabels(
            ["姓名", "性别", "关系", "联系电话", "备注"]
        )
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.member_table.setAlternatingRowColors(True)
        self.member_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.member_table.doubleClicked.connect(self._on_member_double_clicked)
        layout.addWidget(self.member_table)
        self.tabs.addTab(tab, "家庭成员")

    def _build_record_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.record_table = QTableWidget()
        self.record_table.setColumnCount(6)
        self.record_table.setHorizontalHeaderLabels(
            ["成员", "日期", "类别", "指标", "数值", "状态"]
        )
        self.record_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.record_table.setAlternatingRowColors(True)
        self.record_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.record_table)
        self.tabs.addTab(tab, "体检记录")

    def _build_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["成员", "疾病", "确诊日期", "医院", "状态"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.history_table)
        self.tabs.addTab(tab, "病史记录")

    def refresh(self, member_id=None):
        self._search()

    def _on_text_changed(self, text):
        if len(text) >= 2:
            self._search()

    def _search(self):
        keyword = self.search_edit.text().strip()
        if not keyword:
            self._load_all()
            return

        members = self._member_ctrl.search_members(keyword)
        self.member_table.setRowCount(len(members))
        for i, m in enumerate(members):
            self.member_table.setItem(i, 0, QTableWidgetItem(m.name))
            self.member_table.setItem(i, 1, QTableWidgetItem(m.gender))
            self.member_table.setItem(i, 2, QTableWidgetItem(m.relation))
            self.member_table.setItem(i, 3, QTableWidgetItem(m.phone or ""))
            self.member_table.setItem(i, 4, QTableWidgetItem(m.note or ""))

        records = self._record_ctrl.search_records(keyword)
        self.record_table.setRowCount(len(records))
        for i, r in enumerate(records):
            member_name = ""
            m = self._member_ctrl.get_member(r.member_id)
            if m:
                member_name = m.name
            self.record_table.setItem(i, 0, QTableWidgetItem(member_name))
            self.record_table.setItem(i, 1, QTableWidgetItem(r.record_date))
            self.record_table.setItem(i, 2, QTableWidgetItem(r.category))
            self.record_table.setItem(i, 3, QTableWidgetItem(r.indicator_name))
            self.record_table.setItem(i, 4, QTableWidgetItem(
                f"{r.indicator_value} {r.unit}".strip()))
            status = "⚠异常" if r.is_abnormal else "正常"
            self.record_table.setItem(i, 5, QTableWidgetItem(status))

        histories = self._hist_ctrl.search(keyword)
        self.history_table.setRowCount(len(histories))
        for i, h in enumerate(histories):
            member_name = ""
            m = self._member_ctrl.get_member(h.member_id)
            if m:
                member_name = m.name
            self.history_table.setItem(i, 0, QTableWidgetItem(member_name))
            self.history_table.setItem(i, 1, QTableWidgetItem(h.disease_name))
            self.history_table.setItem(i, 2, QTableWidgetItem(h.diagnose_date))
            self.history_table.setItem(i, 3, QTableWidgetItem(h.hospital))
            self.history_table.setItem(i, 4, QTableWidgetItem(h.status))

        total = len(members) + len(records) + len(histories)
        self.hint_label.setText(
            f"搜索「{keyword}」：找到 {total} 条结果 "
            f"（成员 {len(members)}，记录 {len(records)}，病史 {len(histories)}）"
        )

    def _load_all(self):
        members = self._member_ctrl.get_all_members()
        self.member_table.setRowCount(len(members))
        for i, m in enumerate(members):
            self.member_table.setItem(i, 0, QTableWidgetItem(m.name))
            self.member_table.setItem(i, 1, QTableWidgetItem(m.gender))
            self.member_table.setItem(i, 2, QTableWidgetItem(m.relation))
            self.member_table.setItem(i, 3, QTableWidgetItem(m.phone or ""))
            self.member_table.setItem(i, 4, QTableWidgetItem(m.note or ""))

        all_records = []
        for m in members:
            all_records.extend(self._record_ctrl.get_records_by_member(m.id))
        self.record_table.setRowCount(len(all_records))
        for i, r in enumerate(all_records):
            self.record_table.setItem(i, 0, QTableWidgetItem(
                self._member_ctrl.get_member(r.member_id).name if self._member_ctrl.get_member(r.member_id) else ""))
            self.record_table.setItem(i, 1, QTableWidgetItem(r.record_date))
            self.record_table.setItem(i, 2, QTableWidgetItem(r.category))
            self.record_table.setItem(i, 3, QTableWidgetItem(r.indicator_name))
            self.record_table.setItem(i, 4, QTableWidgetItem(
                f"{r.indicator_value} {r.unit}".strip()))
            self.record_table.setItem(i, 5, QTableWidgetItem(
                "⚠异常" if r.is_abnormal else "正常"))

        all_histories = []
        for m in members:
            all_histories.extend(self._hist_ctrl.get_by_member(m.id))
        self.history_table.setRowCount(len(all_histories))
        for i, h in enumerate(all_histories):
            m = self._member_ctrl.get_member(h.member_id)
            self.history_table.setItem(i, 0, QTableWidgetItem(m.name if m else ""))
            self.history_table.setItem(i, 1, QTableWidgetItem(h.disease_name))
            self.history_table.setItem(i, 2, QTableWidgetItem(h.diagnose_date))
            self.history_table.setItem(i, 3, QTableWidgetItem(h.hospital))
            self.history_table.setItem(i, 4, QTableWidgetItem(h.status))

        self.hint_label.setText("提示：输入「高血压」「2024」「白细胞」等关键字进行搜索")

    def _on_member_double_clicked(self, index):
        row = index.row()
        members = self._member_ctrl.get_all_members()
        if row < len(members):
            self.member_clicked.emit(members[row].id)
