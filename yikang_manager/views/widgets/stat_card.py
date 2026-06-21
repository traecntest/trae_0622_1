"""
颐康管家 - 统计卡片组件
用于仪表盘展示关键数据指标的可复用卡片组件。
"""
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class StatCard(QFrame):
    """统计卡片，显示标题、数值和副标题。"""

    def __init__(self, title="", value="", subtitle="", color="#2980b9", parent=None):
        super().__init__(parent)
        self.setObjectName("CardBox")
        self._color = color
        self._title = title
        self._value = value
        self._subtitle = subtitle
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(6)

        self.title_label = QLabel(self._title)
        self.title_label.setStyleSheet(f"color: #7f8c8d; font-size: 13px; border: none;")

        self.value_label = QLabel(self._value)
        font = QFont()
        font.setPointSize(28)
        font.setBold(True)
        self.value_label.setFont(font)
        self.value_label.setStyleSheet(
            f"color: {self._color}; border: none;"
        )

        self.subtitle_label = QLabel(self._subtitle)
        self.subtitle_label.setStyleSheet("color: #95a5a6; font-size: 12px; border: none;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.subtitle_label)

    def set_value(self, value, subtitle=""):
        self.value_label.setText(str(value))
        if subtitle:
            self.subtitle_label.setText(subtitle)

    def set_color(self, color):
        self._color = color
        self.value_label.setStyleSheet(f"color: {color}; border: none;")
