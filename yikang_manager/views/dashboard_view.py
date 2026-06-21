"""
颐康管家 - 仪表盘视图
展示家庭健康概览：成员统计、异常指标、即将到期的提醒等。
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from views.widgets.stat_card import StatCard
from controllers.member_controller import MemberController
from controllers.record_controller import RecordController
from controllers.reminder_controller import ReminderController
from controllers.misc_controller import HistoryController


class DashboardView(QWidget):
    """仪表盘视图。"""

    navigate_requested = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._member_ctrl = MemberController()
        self._record_ctrl = RecordController()
        self._reminder_ctrl = ReminderController()
        self._history_ctrl = HistoryController()
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setSpacing(16)

        title = QLabel("健康仪表盘")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a5276;")
        main_layout.addWidget(title)

        self._build_stat_cards(main_layout)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(12)
        self._build_reminder_panel(bottom_layout)
        self._build_abnormal_panel(bottom_layout)
        main_layout.addLayout(bottom_layout)

        self._build_member_overview(main_layout)

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _build_stat_cards(self, parent_layout):
        card_layout = QHBoxLayout()
        card_layout.setSpacing(12)
        self.card_members = StatCard("家庭成员", "0", "位成员", "#2980b9")
        self.card_records = StatCard("体检记录", "0", "条记录", "#27ae60")
        self.card_abnormal = StatCard("异常指标", "0", "需关注", "#e74c3c")
        self.card_reminders = StatCard("待办提醒", "0", "项待办", "#f39c12")
        for card in [self.card_members, self.card_records, self.card_abnormal, self.card_reminders]:
            card_layout.addWidget(card)
        parent_layout.addLayout(card_layout)

    def _build_reminder_panel(self, parent_layout):
        group = QGroupBox("即将到期的提醒")
        group.setObjectName("CardBox")
        layout = QVBoxLayout(group)

        self.reminder_table = QTableWidget()
        self.reminder_table.setColumnCount(4)
        self.reminder_table.setHorizontalHeaderLabels(["标题", "类型", "时间", "状态"])
        self.reminder_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.reminder_table.setAlternatingRowColors(True)
        self.reminder_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.reminder_table)
        parent_layout.addWidget(group)

    def _build_abnormal_panel(self, parent_layout):
        group = QGroupBox("最近异常指标")
        group.setObjectName("CardBox")
        layout = QVBoxLayout(group)

        self.abnormal_table = QTableWidget()
        self.abnormal_table.setColumnCount(5)
        self.abnormal_table.setHorizontalHeaderLabels(
            ["成员", "指标", "数值", "日期", "参考范围"]
        )
        self.abnormal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.abnormal_table.setAlternatingRowColors(True)
        self.abnormal_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.abnormal_table)
        parent_layout.addWidget(group)

    def _build_member_overview(self, parent_layout):
        group = QGroupBox("家庭成员健康概览")
        group.setObjectName("CardBox")
        layout = QVBoxLayout(group)
        self.member_overview_label = QLabel()
        self.member_overview_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
        layout.addWidget(self.member_overview_label)
        parent_layout.addWidget(group)

    def refresh(self, member_id=None):
        """刷新仪表盘数据。"""
        members = self._member_ctrl.get_all_members()
        self.card_members.set_value(len(members), "位家庭成员")

        from models.health_record import HealthRecord
        total_records = 0
        abnormal_items = []
        for m in members:
            records = self._record_ctrl.get_records_by_member(m.id)
            total_records += len(records)
            for r in self._record_ctrl.get_latest_abnormal(m.id, limit=3):
                abnormal_items.append((m.name, r))

        total_abnormal = HealthRecord.abnormal_count()
        self.card_records.set_value(total_records, "条体检记录")
        self.card_abnormal.set_value(total_abnormal, "项需关注")

        reminders = self._reminder_ctrl.get_pending_reminders()
        self.card_reminders.set_value(len(reminders), "项待办提醒")

        upcoming = self._reminder_ctrl.get_upcoming(days=7)
        self.reminder_table.setRowCount(len(upcoming))
        for i, r in enumerate(upcoming):
            member_name = ""
            if r.member_id:
                m = self._member_ctrl.get_member(r.member_id)
                if m:
                    member_name = m.name
            self.reminder_table.setItem(i, 0, QTableWidgetItem(f"{r.title} ({member_name})"))
            self.reminder_table.setItem(i, 1, QTableWidgetItem(r.remind_type))
            self.reminder_table.setItem(i, 2, QTableWidgetItem(r.remind_time))
            self.reminder_table.setItem(i, 3, QTableWidgetItem("待办"))

        self.abnormal_table.setRowCount(len(abnormal_items))
        for i, (name, r) in enumerate(abnormal_items):
            self.abnormal_table.setItem(i, 0, QTableWidgetItem(name))
            self.abnormal_table.setItem(i, 1, QTableWidgetItem(r.indicator_name))
            self.abnormal_table.setItem(i, 2, QTableWidgetItem(
                f"{r.indicator_value} {r.unit}"))
            self.abnormal_table.setItem(i, 3, QTableWidgetItem(r.record_date))
            self.abnormal_table.setItem(i, 4, QTableWidgetItem(r.reference_range))

        overview_lines = []
        for m in members:
            summary = self._member_ctrl.get_member_summary(m.id)
            line = (
                f"  • {m.name}（{m.relation}）："
                f"{summary['record_count']}条记录，"
                f"{summary['abnormal_count']}项异常，"
                f"{summary['medication_count']}种用药，"
                f"{summary['history_count']}条病史，"
                f"最近体检 {summary['latest_record_date']}"
            )
            overview_lines.append(line)
        self.member_overview_label.setText("\n".join(overview_lines))
