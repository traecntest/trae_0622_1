"""
颐康管家 - 提醒服务模块
基于 APScheduler 实现后台定时任务，根据录入的服药频率或复诊日期，
在桌面右下角弹出通知气泡，确保不遗漏重要医疗安排。
"""
import logging
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from models.reminder import Reminder

logger = logging.getLogger(__name__)


class ReminderService:
    """后台提醒调度服务。"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._scheduler = None
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._scheduler = BackgroundScheduler()
        self._initialized = False

    def start(self):
        """启动调度器并加载所有待执行的提醒。"""
        if self._initialized:
            return
        try:
            self._scheduler.start()
            self._initialized = True
            self.reload_all()
            logger.info("提醒服务已启动")
        except Exception as e:
            logger.error(f"提醒服务启动失败: {e}")

    def reload_all(self):
        """重新加载所有未完成的提醒任务。"""
        if not self._initialized:
            return
        for job in self._scheduler.get_jobs():
            if job.id.startswith("reminder_"):
                job.remove()
        for reminder in Reminder.pending():
            self._schedule_reminder(reminder)

    def _schedule_reminder(self, reminder):
        """为单条提醒创建调度任务。"""
        try:
            remind_time = datetime.strptime(reminder.remind_time, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return

        job_id = f"reminder_{reminder.id}"
        if remind_time <= datetime.now() and reminder.repeat_rule != "daily":
            self._fire_notification(reminder)
            return

        if reminder.repeat_rule == "daily":
            trigger = CronTrigger(hour=remind_time.hour, minute=remind_time.minute)
            self._scheduler.add_job(
                self._fire_notification, trigger,
                args=[reminder], id=job_id, replace_existing=True,
            )
        else:
            trigger = DateTrigger(run_date=remind_time)
            self._scheduler.add_job(
                self._fire_notification, trigger,
                args=[reminder], id=job_id, replace_existing=True,
            )

    def _fire_notification(self, reminder):
        """触发桌面通知。"""
        try:
            from utils.notifier import notifier
            title = f"【{reminder.remind_type}】{reminder.title}"
            content = reminder.content or "请及时查看"
            notifier.show_message(title, content)
        except Exception as e:
            logger.error(f"通知发送失败: {e}")

    def add_reminder(self, reminder):
        """新增一条提醒调度。"""
        if reminder.is_done:
            return
        self._schedule_reminder(reminder)

    def remove_reminder(self, reminder_id):
        """移除一条提醒调度。"""
        job_id = f"reminder_{reminder_id}"
        try:
            self._scheduler.remove_job(job_id)
        except Exception:
            pass

    def shutdown(self):
        """关闭调度器。"""
        if self._initialized and self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._initialized = False


reminder_service = ReminderService()
