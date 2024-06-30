from datetime import datetime, timedelta
from .extensions import scheduler, db
from .models import Diary, Color
from .langchain.responses import convert_diary_to_colors


def process_daily_diary():
    print("Processing")
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    with scheduler.app.app_context():
        # diaries = Diary.query.filter_by(date=yesterday).all()
        diaries = Diary.query.all()
        for diary in diaries:
            existing_colors = Color.query.filter_by(diary_id=diary.diary_id).all()
            if existing_colors:
                print(diary.diary_id, " colors already exist.")
                continue

            if len(diary.content) < 20:
                color = Color(
                    user_id=diary.user_id,
                    diary_id=diary.diary_id,
                    color="Gray",
                    content=diary.content,
                )
                db.session.add(color)
            else:
                color_objects = convert_diary_to_colors(diary.content)
                for color_obj in color_objects:
                    color = Color(
                        user_id=diary.user_id,
                        diary_id=diary.diary_id,
                        color=color_obj["color"],
                        content=color_obj["content"],
                    )
                    db.session.add(color)

        db.session.commit()
