"""
颐康管家 - 主窗口
采用 HIS 系统专业感设计：左侧导航栏、中间数据展示主窗口、右侧快捷操作区。
集成仪表盘、档案中心、数据分析、提醒设置等视图，并支持模糊搜索。
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QStackedWidget, QFrame, QLineEdit, QMessageBox, QStatusBar, QMenu,
    QSystemTrayIcon, QApplication, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon

from config import APP_NAME, APP_VERSION, APP_SUBTITLE, APP_STYLE
from views.dashboard_view import DashboardView
from views.archive_view import ArchiveView
from views.analysis_view import AnalysisView
from views.reminder_view import ReminderView
from views.search_view import SearchView
from views.dialogs import OCRImportDialog
from utils.notifier import Notifier, create_app_icon
from services.reminder_service import reminder_service


class MainWindow(QMainWindow):
    """颐康管家主窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} - {APP_SUBTITLE}")
        self.setMinimumSize(1200, 750)
        self.setWindowIcon(create_app_icon())

        self._views = {}
        self._setup_ui()
        self._setup_tray()
        self._setup_statusbar()

        reminder_service.start()
        self._refresh_all()

    def _setup_ui(self):
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._build_nav_panel(main_layout)
        self._build_center_panel(main_layout)
        self._build_quick_panel(main_layout)

        self.setStyleSheet(APP_STYLE)

    def _build_nav_panel(self, parent_layout):
        nav = QFrame()
        nav.setObjectName("NavPanel")
        nav.setFixedWidth(200)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(8, 16, 8, 8)
        nav_layout.setSpacing(4)

        title = QLabel("颐康管家")
        title.setObjectName("NavTitle")
        nav_layout.addWidget(title)
        subtitle = QLabel("家庭健康管理")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 0 8px 16px 8px;")
        nav_layout.addWidget(subtitle)

        nav_items = [
            ("仪表盘", 0),
            ("档案中心", 1),
            ("数据分析", 2),
            ("提醒设置", 3),
            ("全局搜索", 4),
        ]
        self.nav_buttons = []
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        for text, idx in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setCursor(Qt.PointingHandCursor)
            self.button_group.addButton(btn, idx)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        self.button_group.buttonClicked.connect(self._on_nav_clicked)
        self.nav_buttons[0].setChecked(True)

        nav_layout.addStretch()

        version_label = QLabel(f"v{APP_VERSION}\n本地加密存储")
        version_label.setStyleSheet("color: #566573; font-size: 11px; padding: 8px;")
        version_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(version_label)

        parent_layout.addWidget(nav)

    def _build_center_panel(self, parent_layout):
        center = QFrame()
        center.setStyleSheet("background-color: #f0f4f8;")
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #d5dbdb;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        self.page_title = QLabel("健康仪表盘")
        self.page_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a5276;")
        header_layout.addWidget(self.page_title)
        header_layout.addStretch()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 搜索疾病、指标、日期...")
        self.search_bar.setFixedWidth(300)
        self.search_bar.returnPressed.connect(self._quick_search)
        header_layout.addWidget(self.search_bar)

        center_layout.addWidget(header)

        self.stack = QStackedWidget()
        self.dashboard = DashboardView()
        self.archive = ArchiveView()
        self.analysis = AnalysisView()
        self.reminder = ReminderView()
        self.search = SearchView()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.archive)
        self.stack.addWidget(self.analysis)
        self.stack.addWidget(self.reminder)
        self.stack.addWidget(self.search)

        center_layout.addWidget(self.stack, 1)
        parent_layout.addWidget(center, 1)

    def _build_quick_panel(self, parent_layout):
        panel = QFrame()
        panel.setFixedWidth(220)
        panel.setStyleSheet("background-color: #ffffff; border-left: 1px solid #d5dbdb;")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(12, 16, 12, 12)
        panel_layout.setSpacing(8)

        quick_title = QLabel("快捷操作")
        quick_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a5276; padding-bottom: 8px;")
        panel_layout.addWidget(quick_title)

        actions = [
            ("📝  新增家庭成员", self._quick_add_member),
            ("📋  新增体检记录", self._quick_add_record),
            ("🔬  OCR导入报告", self._quick_ocr_import),
            ("⏰  新增提醒", self._quick_add_reminder),
            ("📊  查看趋势分析", lambda: self._switch_view(2)),
            ("🔍  全局搜索", self._quick_search),
        ]
        for text, callback in actions:
            btn = QPushButton(text)
            btn.setObjectName("QuickButton")
            btn.clicked.connect(callback)
            panel_layout.addWidget(btn)

        panel_layout.addStretch()

        info_box = QFrame()
        info_box.setStyleSheet(
            "background-color: #ebf5fb; border-radius: 8px; padding: 12px;"
        )
        info_layout = QVBoxLayout(info_box)
        info_title = QLabel("🔒 数据安全")
        info_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a5276;")
        info_text = QLabel("所有健康数据均采用\nAES加密存储于本地，\n不上传云端。")
        info_text.setStyleSheet("font-size: 11px; color: #566573;")
        info_layout.addWidget(info_title)
        info_layout.addWidget(info_text)
        panel_layout.addWidget(info_box)

        parent_layout.addWidget(panel)

    def _setup_tray(self):
        if Notifier.is_supported():
            self.tray = QSystemTrayIcon(create_app_icon(), self)
            self.tray.setToolTip(f"{APP_NAME} - 运行中")
            menu = QMenu(self)
            show_action = QAction("显示主窗口", self)
            show_action.triggered.connect(self._show_window)
            minimize_action = QAction("最小化到托盘", self)
            minimize_action.triggered.connect(self._minimize_to_tray)
            quit_action = QAction("完全退出", self)
            quit_action.triggered.connect(self._quit_app)
            menu.addAction(show_action)
            menu.addAction(minimize_action)
            menu.addSeparator()
            menu.addAction(quit_action)
            self.tray.setContextMenu(menu)
            self.tray.activated.connect(self._on_tray_activated)
            self.tray.show()
            Notifier._tray = self.tray
            Notifier.show_message(APP_NAME, f"{APP_NAME}已启动，正在守护您的家庭健康。")

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _minimize_to_tray(self):
        self.hide()
        if hasattr(self, "tray") and self.tray.isVisible():
            Notifier.show_message(
                APP_NAME, "程序已最小化到系统托盘，后台提醒持续运行。"
            )

    def _setup_statusbar(self):
        sb = QStatusBar()
        sb.showMessage("就绪 - 数据已加密保护")
        self.setStatusBar(sb)

    def _on_nav_clicked(self, button):
        idx = self.button_group.id(button)
        if idx >= 0:
            self._switch_view(idx)

    def _switch_view(self, index):
        self.stack.setCurrentIndex(index)
        titles = ["健康仪表盘", "档案中心", "数据分析", "提醒设置", "全局搜索"]
        self.page_title.setText(titles[index])
        btn = self.button_group.button(index)
        if btn and not btn.isChecked():
            self.button_group.blockSignals(True)
            btn.setChecked(True)
            self.button_group.blockSignals(False)
        view = self.stack.widget(index)
        if hasattr(view, "refresh"):
            view.refresh()

    def _refresh_all(self):
        self.dashboard.refresh()
        self.archive.refresh()
        self.analysis.refresh()
        self.reminder.refresh()
        self.search.refresh()

    def _quick_add_member(self):
        self._switch_view(1)
        self.archive._add_member()

    def _quick_add_record(self):
        self._switch_view(1)
        if not self.archive._current_member_id:
            QMessageBox.information(self, "提示", "请先在档案中心选择一位家庭成员")
            return
        self.archive._add_record()

    def _quick_ocr_import(self):
        from controllers.member_controller import MemberController
        members = MemberController().get_all_members()
        if not members:
            QMessageBox.warning(self, "提示", "请先创建家庭成员")
            return
        dlg = OCRImportDialog(self, member_id=members[0].id)
        if dlg.exec():
            self._refresh_all()

    def _quick_add_reminder(self):
        self._switch_view(3)
        self.reminder._add_reminder()

    def _quick_search(self):
        keyword = self.search_bar.text().strip()
        self._switch_view(4)
        if keyword:
            self.search.search_edit.setText(keyword)
            self.search._search()

    def _quit_app(self):
        self._force_quit = True
        reminder_service.shutdown()
        if hasattr(self, "tray"):
            self.tray.hide()
        QApplication.quit()

    def closeEvent(self, event):
        if getattr(self, "_force_quit", False):
            event.accept()
            return
        reply = QMessageBox.question(
            self, "确认退出",
            "确定要退出颐康管家吗？\n\n"
            "选择「最小化」将隐藏到系统托盘，后台提醒继续运行。\n"
            "选择「退出」将完全关闭程序。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        if reply == QMessageBox.Yes:
            self._force_quit = True
            reminder_service.shutdown()
            if hasattr(self, "tray"):
                self.tray.hide()
            event.accept()
        else:
            self._minimize_to_tray()
            event.ignore()
