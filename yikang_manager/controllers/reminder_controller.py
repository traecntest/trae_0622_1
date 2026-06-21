"""
颐康管家 - 提醒事项控制器
协调提醒的增删改查，并与提醒服务同步调度任务。
"""
from models.reminder import Reminder
from services.reminder_service import reminder_service


class ReminderController:
    """提醒管理控制器。"""

    def get_all_reminders(self):
        return Reminder.all()

    def get_pending_reminders(self):
        return Reminder.pending()

    def get_upcoming(self, days=7):
        return Reminder.upcoming(days)

    def get_reminders_by_member(self, member_id):
        return Reminder.by_member(member_id)

    def save_reminder(self, data):
        reminder = Reminder(**data)
        reminder.save()
        reminder_service.add_reminder(reminder)
        return reminder

    def delete_reminder(self, reminder_id):
        reminder_service.remove_reminder(reminder_id)
        reminder = Reminder.get(reminder_id)
        if reminder:
            return reminder.delete()
        return 0

    def mark_done(self, reminder_id, done=True):
        reminder = Reminder.get(reminder_id)
        if reminder:
            reminder.mark_done(done)
            if done:
                reminder_service.remove_reminder(reminder_id)
            return True
        return False
