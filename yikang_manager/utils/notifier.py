"""
颐康管家 - 桌面通知工具模块
利用系统托盘图标弹出气泡通知，用于服药、复诊等提醒。
"""
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QAction
from PySide6.QtCore import QObject, Signal


def create_app_icon():
    """动态生成应用图标（绿色十字健康标志）。"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor("#2980b9"))
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#ecf0f1"))
    painter.drawRect(26, 10, 12, 44)
    painter.drawRect(10, 26, 44, 12)
    painter.end()
    return QIcon(pixmap)


class Notifier(QObject):
    """系统托盘通知器。"""

    notification_triggered = Signal(str, str)

    _tray = None

    @classmethod
    def init_tray(cls, parent=None):
        """初始化系统托盘图标。"""
        if cls._tray is None:
            cls._tray = QSystemTrayIcon(create_app_icon(), parent)
            cls._tray.setToolTip("颐康管家 - 健康管理运行中")
            menu = parent.tray_menu if parent and hasattr(parent, "tray_menu") else None
            cls._tray.show()
        return cls._tray

    @classmethod
    def show_message(cls, title, message, icon_type=QSystemTrayIcon.Information):
        """弹出桌面气泡通知。"""
        if cls._tray is not None and cls._tray.isVisible():
            cls._tray.showMessage(title, message, icon_type, 10000)
        cls.notification_triggered.emit(title, message)

    @classmethod
    def is_supported(cls):
        return QSystemTrayIcon.isSystemTrayAvailable()


notifier = Notifier()
