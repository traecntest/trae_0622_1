"""
颐康管家 - 程序入口
启动桌面健康管理系统主程序。
"""
import sys
import os
import signal
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("YikangManager")


def main():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("颐康管家")
    app.setApplicationVersion("1.0.0")
    app.setQuitOnLastWindowClosed(True)

    from services.seed_data import init_seed_data
    init_seed_data()
    logger.info("数据初始化完成")

    from views.main_window import MainWindow

    window = MainWindow()
    window.show()

    def cleanup():
        logger.info("正在清理资源...")
        try:
            from services.reminder_service import reminder_service
            reminder_service.shutdown()
        except Exception as e:
            logger.warning(f"清理异常: {e}")

    app.aboutToQuit.connect(cleanup)

    logger.info("颐康管家启动成功")
    exit_code = app.exec()
    logger.info(f"应用退出，退出码: {exit_code}")
    os._exit(exit_code)


if __name__ == "__main__":
    main()
