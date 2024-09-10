from datetime import datetime, timedelta
from .extensions import scheduler, db
from .models import Diary, Color
from .langchain.responses import (
    convert_diary_html_to_text,
    convert_diary_to_colors,
    convert_diary_to_summary,
)


def paint_daily_diary():
    print("Paint diary")
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    with scheduler.app.app_context():
        # diaries = Diary.query.filter_by(date=yesterday).all()
        diaries = Diary.query.all()
        for diary in diaries:
            try:
                print(diary.diary_id)
                existing_colors = Color.query.filter_by(diary_id=diary.diary_id).all()
                diary_content = ""
                if len(diary.content) > 100:
                    diary_content = convert_diary_html_to_text(diary.content)
                print(diary_content)

                if not existing_colors:
                    if len(diary_content) < 20:
                        print("too short not paint")
                        color = Color(
                            user_id=diary.user_id,
                            diary_id=diary.diary_id,
                            color="White",
                            content=diary.content,
                        )
                        db.session.add(color)
                    else:
                        color_objects = convert_diary_to_colors(diary_content)
                        for color_obj in color_objects:
                            color = Color(
                                user_id=diary.user_id,
                                diary_id=diary.diary_id,
                                color=color_obj["color"],
                                content=color_obj["content"],
                            )
                            db.session.add(color)
                    db.session.commit()  # Commit after adding colors

                if diary.summary == "":
                    print("Summary diary: ", diary.diary_id)
                    diary.status = "PAINTING"
                    if len(diary_content) > 20:
                        summary_item = convert_diary_to_summary(diary_content)
                        print("summary result:", summary_item["tag"], summary_item["summary"])
                        diary.tag = summary_item["tag"]
                        diary.summary = summary_item["summary"]
                        diary.summary_embedding = summary_item["summary_embedding"]
                    else:
                        diary.tag = "其他"
                    db.session.commit()  # Commit after updating diary
            except Exception as e:
                print(f"An error occurred for diary {diary.diary_id}: {e}")
                db.session.rollback()


def refresh_daily_diary():
    with scheduler.app.app_context():
        diaries = Diary.query.filter_by(status="PAINTING").all()
        for diary in diaries:
            diary.status = "COMPLETED"

        db.session.commit()
