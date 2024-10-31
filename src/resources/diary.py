from datetime import datetime
from collections import defaultdict
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import User, Paletter, Diary, DiaryEntry, Color
from src.langchain.responses import get_diary_reply
from src.constants.paletter_table import paletter_code_table

parser = reqparse.RequestParser()


class DiaryResource(Resource):
    def get(self, diary_id):
        user_id = g.user_id

        # Today's diary
        if diary_id == 0:
            today = datetime.now().date()

            diary = Diary.query.filter_by(user_id=user_id, date=today).first()

            if not diary:
                diary = Diary(user_id=user_id)
                db.session.add(diary)
                db.session.commit()

                return {
                    "diary_info": diary.to_dict(),
                    "diary_entries": [],
                }, 200

            diary_id = diary.diary_id
        else:
            diary = Diary.query.filter_by(
                user_id=user_id, diary_id=diary_id
            ).first_or_404()

        diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

        return {
            "diary_info": diary.to_dict(),
            "diary_entries": [entry.to_dict() for entry in diary_entries],
        }, 200

    def put(self, diary_id):
        user_id = g.user_id

        user = User.query.get_or_404(user_id)
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()
        diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

        if not diary_entries:
            return {"message": "Diary is empty."}, 404

        # 計算每種emotion的總字數和最新時間
        emotion_stats = defaultdict(lambda: {"chars": 0, "latest_time": datetime.min})

        for entry in diary_entries:
            emotion = entry.emotion
            char_count = len(entry.content)

            emotion_stats[emotion]["chars"] += char_count
            if entry.created_time > emotion_stats[emotion]["latest_time"]:
                emotion_stats[emotion]["latest_time"] = entry.created_time

        # 找出主要emotion
        max_chars = max(stat["chars"] for stat in emotion_stats.values())
        dominant_emotions = [
            emotion
            for emotion, stat in emotion_stats.items()
            if stat["chars"] == max_chars
        ]

        # 如果有多個相同字數的emotion，選擇最晚的created_time
        if len(dominant_emotions) > 1:
            dominant_emotion = max(
                dominant_emotions, key=lambda e: emotion_stats[e]["latest_time"]
            )
        else:
            dominant_emotion = dominant_emotions[0]

        user_name = user.name
        diary_content = "\n\n".join(
            [
                f"{entry.created_time.strftime('%H:%M')} - {entry.content}"
                for entry in diary_entries
            ]
        )

        paletter_code = dominant_emotion + "-1"
        paletter_name = paletter_code_table[paletter_code]

        reply_content = get_diary_reply(
            user_name, paletter_code, paletter_name, "30", "5", diary_content
        )

        diary.reply_paletter_code = paletter_code
        diary.reply_content = reply_content

        db.session.add(diary)
        db.session.commit()

        return diary.to_dict(), 200

    def delete(self, diary_id):
        user_id = g.user_id
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        db.session.delete(diary)
        db.session.commit()

        return "", 200


class DiaryListResource(Resource):
    def get(self, page):
        user_id = g.user_id

        try:
            page = int(page)
        except ValueError:
            return {"error": "Invalid page format."}, 400

        if page < 1:
            return {"error": "Page number must be greater than or equal to 1."}, 400

        pagination = (
            Diary.query.filter_by(user_id=user_id)
            .order_by(Diary.date.desc())
            .paginate(page=page, per_page=20, error_out=False)
        )

        diaries = []
        for diary in pagination.items:
            color_items = Color.query.filter_by(
                user_id=user_id, diary_id=diary.diary_id
            ).all()
            color_list = [c.color for c in color_items]
            diary.to_limited_dict()
            diary_dict = diary.to_limited_dict()
            diary_dict["colors"] = color_list
            diaries.append(diary_dict)

        next_page = pagination.page + 1 if pagination.has_next else -1

        return {
            "diaries": diaries,
            "next_page": next_page,
            "total_pages": pagination.pages,
        }, 200
