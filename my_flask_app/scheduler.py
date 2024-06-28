from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from .models import Diary, db


def process_daily_diary():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    diaries = Diary.query.filter_by(date=yesterday).all()
    for diary in diaries:
        if diary.status == "編輯中":
            diary.status = "上色中"

    db.session.commit()


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_daily_diary, "cron", hour=0, minute=0)
    scheduler.start()
