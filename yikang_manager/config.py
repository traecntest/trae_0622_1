"""
颐康管家 - 系统配置模块
集中管理应用级别的常量与配置项。
"""
import os

APP_NAME = "颐康管家"
APP_VERSION = "1.0.0"
APP_SUBTITLE = "家庭健康数据管理平台"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
RESOURCE_DIR = os.path.join(BASE_DIR, "resources")

DB_PATH = os.path.join(DATA_DIR, "yikang.db")
KEY_PATH = os.path.join(DATA_DIR, "yikang.key")
REPORT_DIR = os.path.join(DATA_DIR, "reports")

for _d in (DATA_DIR, REPORT_DIR, RESOURCE_DIR):
    os.makedirs(_d, exist_ok=True)

DB_NAME = "yikang.db"

ENCRYPTED_FIELDS = {
    "family_members": ["name", "id_card", "phone", "relation"],
    "health_records": ["indicator_value", "report_image", "note"],
    "medications": ["drug_name", "dosage", "note"],
    "reminders": ["title", "content"],
}

NORMAL_RANGES = {
    "白细胞计数": (3.5, 9.5, "10^9/L"),
    "红细胞计数": (3.8, 5.1, "10^12/L"),
    "血红蛋白": (115, 150, "g/L"),
    "血小板计数": (125, 350, "10^9/L"),
    "空腹血糖": (3.9, 6.1, "mmol/L"),
    "总胆固醇": (3.1, 5.2, "mmol/L"),
    "甘油三酯": (0.4, 1.7, "mmol/L"),
    "收缩压": (90, 120, "mmHg"),
    "舒张压": (60, 80, "mmHg"),
    "尿蛋白": (0, 0, "mg/L"),
    "尿酸": (208, 428, "umol/L"),
    "丙氨酸氨基转移酶": (7, 40, "U/L"),
}

INDICATOR_CATEGORIES = {
    "血常规": ["白细胞计数", "红细胞计数", "血红蛋白", "血小板计数"],
    "生化": ["空腹血糖", "总胆固醇", "甘油三酯", "尿酸", "丙氨酸氨基转移酶"],
    "血压": ["收缩压", "舒张压"],
    "尿常规": ["尿蛋白"],
}

APP_STYLE = """
QMainWindow, QWidget#CentralWidget {
    background-color: #f0f4f8;
}
QLabel#AppTitle {
    font-size: 22px;
    font-weight: bold;
    color: #1a5276;
}
QLabel#NavTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    padding: 8px;
}
QPushButton#NavButton {
    text-align: left;
    padding: 12px 16px;
    font-size: 14px;
    color: #d4e6f1;
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
QPushButton#NavButton:hover {
    background-color: #2c3e50;
    color: #ffffff;
}
QPushButton#NavButton:checked {
    background-color: #2980b9;
    color: #ffffff;
    font-weight: bold;
}
QPushButton#QuickButton {
    padding: 18px;
    font-size: 13px;
    background-color: #ffffff;
    border: 1px solid #d5dbdb;
    border-radius: 8px;
    text-align: left;
}
QPushButton#QuickButton:hover {
    background-color: #ebf5fb;
    border: 1px solid #3498db;
}
QPushButton#PrimaryButton {
    background-color: #2980b9;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-size: 13px;
}
QPushButton#PrimaryButton:hover { background-color: #21618c; }
QPushButton#DangerButton {
    background-color: #c0392b;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
}
QPushButton#DangerButton:hover { background-color: #922b21; }
QGroupBox#CardBox {
    background-color: #ffffff;
    border: 1px solid #d5dbdb;
    border-radius: 8px;
    margin-top: 12px;
    font-size: 14px;
    font-weight: bold;
    color: #1a5276;
}
QGroupBox#CardBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QLineEdit, QComboBox, QSpinBox, QDateEdit, QDateTimeEdit {
    padding: 6px;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    background-color: #ffffff;
}
QTreeWidget, QTableWidget {
    border: 1px solid #d5dbdb;
    border-radius: 4px;
    background-color: #ffffff;
    alternate-background-color: #f8f9fa;
}
QHeaderView::section {
    background-color: #2c3e50;
    color: white;
    padding: 6px;
    border: none;
    font-weight: bold;
}
QStatusBar {
    background-color: #2c3e50;
    color: #ecf0f1;
}
QFrame#NavPanel {
    background-color: #1b2631;
}
"""

OCR_ENGINE_PRIORITY = ["paddle", "tesseract"]
OCR_AVAILABLE = True
