"""
颐康管家 - 提醒设置视图
集中管理所有家庭成员的服药、复诊等提醒事项，
支持新增、标记完成、删除操作，并展示即将到期的提醒列表。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal

from controllers.member_controller import MemberController
from controllers.reminder_controller import ReminderController
from views.dialogs import ReminderDialog


class ReminderView(QWidget):
    """提醒设置视图。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._member_ctrl = MemberController()
        self._reminder_ctrl = ReminderController()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        title = QLabel("提醒管理")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a5276;")
        layout.addWidget(title)

        splitter = QSplitter(Qt.Vertical)

        upcoming_group = QGroupBox("即将到期提醒（7天内）")
        upcoming_group.setObjectName("CardBox")
        upcoming_layout = QVBoxLayout(upcoming_group)
        self.upcoming_table = QTableWidget()
        self.upcoming_table.setColumnCount(5)
        self.upcoming_table.setHorizontalHeaderLabels(
            ["成员", "标题", "类型", "时间", "内容"]
        )
        self.upcoming_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.upcoming_table.setAlternatingRowColors(True)
        self.upcoming_table.setEditTriggers(QTableWidget.NoEditTriggers)
        upcoming_layout.addWidget(self.upcoming_table)
        splitter.addWidget(upcoming_group)

        all_group = QGroupBox("全部提醒事项")
        all_group.setObjectName("CardBox")
        all_layout = QVBoxLayout(all_group)

        ctrl_layout = QHBoxLayout()
        ctrl_layout.addWidget(QLabel("筛选成员："))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部成员", None)
        self.filter_combo.currentIndexChanged.connect(self._refresh_table)
        ctrl_layout.addWidget(self.filter_combo, 1)

        self.add_btn = QPushButton("新增提醒")
        self.add_btn.setObjectName("PrimaryButton")
        self.add_btn.clicked.connect(self._add_reminder)
        self.done_btn = QPushButton("标记完成")
        self.done_btn.clicked.connect(self._mark_done)
        self.del_btn = QPushButton("删除")
        self.del_btn.setObjectName("DangerButton")
        self.del_btn.clicked.connect(self._delete_reminder)
        ctrl_layout.addWidget(self.add_btn)
        ctrl_layout.addWidget(self.done_btn)
        ctrl_layout.addWidget(self.del_btn)
        all_layout.addLayout(ctrl_layout)

        self.all_table = QTableWidget()
        self.all_table.setColumnCount(6)
        self.all_table.setHorizontalHeaderLabels(
            ["成员", "标题", "类型", "时间", "重复", "状态"]
        )
        self.all_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.all_table.setAlternatingRowColors(True)
        self.all_table.setEditTriggers(QTableWidget.NoEditTriggers)
        all_layout.addWidget(self.all_table)
        splitter.addWidget(all_group)

        splitter.setSizes([200, 300])
        layout.addWidget(splitter, 1)

    def refresh(self, member_id=None):
        self._load_filter_combo()
        self._refresh_upcoming()
        self._refresh_table()

    def _load_filter_combo(self):
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        self.filter_combo.addItem("全部成员", None)
        members = self._member_ctrl.get_all_members()
        for m in members:
            self.filter_combo.addItem(f"{m.name}（{m.relation}）", m.id)
        self.filter_combo.blockSignals(False)

    def _refresh_upcoming(self):
        upcoming = self._reminder_ctrl.get_upcoming(days=7)
        self.upcoming_table.setRowCount(len(upcoming))
        for i, r in enumerate(upcoming):
            name = ""
            if r.member_id:
                m = self._member_ctrl.get_member(r.member_id)
                if m:
                    name = m.name
            self.upcoming_table.setItem(i, 0, QTableWidgetItem(name))
            self.upcoming_table.setItem(i, 1, QTableWidgetItem(r.title))
            self.upcoming_table.setItem(i, 2, QTableWidgetItem(r.remind_type))
            self.upcoming_table.setItem(i, 3, QTableWidgetItem(r.remind_time))
            self.upcoming_table.setItem(i, 4, QTableWidgetItem(r.content or ""))

    def _refresh_table(self):
        filter_id = self.filter_combo.currentData()
        if filter_id:
            reminders = self._reminder_ctrl.get_reminders_by_member(filter_id)
        else:
            reminders = self._reminder_ctrl.get_all_reminders()
        reminders.sort(key=lambda r: r.remind_time, reverse=True)
        self.all_table.setRowCount(len(reminders))
        for i, r in enumerate(reminders):
            name = ""
            if r.member_id:
                m = self._member_ctrl.get_member(r.member_id)
                if m:
                    name = m.name
            self.all_table.setItem(i, 0, QTableWidgetItem(name))
            self.all_table.setItem(i, 1, QTableWidgetItem(r.title))
            self.all_table.setItem(i, 2, QTableWidgetItem(r.remind_type))
            self.all_table.setItem(i, 3, QTableWidgetItem(r.remind_time))
            repeat = {"once": "仅一次", "daily": "每日"}.get(r.repeat_rule, r.repeat_rule)
            self.all_table.setItem(i, 4, QTableWidgetItem(repeat))
            status_item = QTableWidgetItem("已完成" if r.is_done else "待办")
            if r.is_done:
                status_item.setForeground(Qt.gray)
            else:
                status_item.setForeground(Qt.red)
            self.all_table.setItem(i, 5, status_item)

    def _add_reminder(self):
        members = self._member_ctrl.get_all_members()
        if not members:
            QMessageBox.warning(self, "提示", "请先创建家庭成员")
            return
        dlg = ReminderDialog(self, member_id=members[0].id)
        if dlg.exec():
            data = dlg.get_data()
            self._reminder_ctrl.save_reminder(data)
            self._refresh_upcoming()
            self._refresh_table()

    def _mark_done(self):
        row = self.all_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条提醒")
            return
        filter_id = self.filter_combo.currentData()
        if filter_id:
            reminders = self._reminder_ctrl.get_reminders_by_member(filter_id)
        else:
            reminders = self._reminder_ctrl.get_all_reminders()
        reminders.sort(key=lambda r: r.remind_time, reverse=True)
        if row < len(reminders):
            self._reminder_ctrl.mark_done(reminders[row].id)
            self._refresh_upcoming()
            self._refresh_table()

    def _delete_reminder(self):
        row = self.all_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "提示", "请先选择一条提醒")
            return
        reply = QMessageBox.question(self, "确认删除", "确定删除这条提醒吗？",
                                      QMessageBox.Yes | QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        filter_id = self.filter_combo.currentData()
        if filter_id:
            reminders = self._reminder_ctrl.get_reminders_by_member(filter_id)
        else:
            reminders = self._reminder_ctrl.get_all_reminders()
        reminders.sort(key=lambda r: r.remind_time, reverse=True)
        if row < len(reminders):
            self._reminder_ctrl.delete_reminder(reminders[row].id)
            self._refresh_upcoming()
            self._refresh_table()
