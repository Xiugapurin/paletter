import uuid
from datetime import datetime
from calendar import monthrange
from flask import g
from flask_restful import Resource
from sqlalchemy import extract
from src.models import Diary, Color
from src.constants.paletter_table import paletter_code_table


class EmotionResource(Resource):
    def get(self, color):
        user_id = g.user_id

        if color not in [
            "Red",
            "Orange",
            "Yellow",
            "Green",
            "Blue",
            "Indigo",
            "Purple",
            "Gray",
            "White",
        ]:
            return {"error": "Invalid color."}, 400

        colors = Color.query.filter_by(user_id=user_id, color=color).all()
        diary_ids = [color_entry.diary_id for color_entry in colors]

        diaries = (
            Diary.query.filter(Diary.diary_id.in_(diary_ids))
            .order_by(Diary.date.desc())
            .all()
        )

        result = []
        for diary in diaries:
            color_entry = next(
                (ce for ce in colors if ce.diary_id == diary.diary_id), None
            )
            if color_entry:
                result.append(
                    {
                        "diary_id": diary.diary_id,
                        "date": diary.date.isoformat().replace("-", " / "),
                        "tag": diary.tag,
                        "content": color_entry.content,
                    }
                )

        return {"diaries": result}, 200


class EmotionListResource(Resource):
    def get(self, year, month):
        user_id = g.user_id

        try:
            year = int(year)
            month = int(month)
        except ValueError:
            return {"error": "Invalid year or month format."}, 400

        if month < 1 or month > 12:
            return {"error": "Invalid month."}, 400

        if year < 1900 or year > datetime.now().year + 1:
            return {"error": "Invalid year."}, 400

        days_in_month = monthrange(year, month)[1]
        current_date = datetime.now().date()
        if year == current_date.year and month == current_date.month:
            days_in_month = current_date.day

        diary_list = [
            {
                "diary_id": -1,
                "date": f"{year}-{month:02d}-{str(day).zfill(2)}",
                "emotion": "None",
                "paletter_code": "None",
            }
            for day in range(1, days_in_month + 1)
        ]

        emotion_counts = {
            "Red": 0,
            "Orange": 0,
            "Yellow": 0,
            "Green": 0,
            "Blue": 0,
            "Indigo": 0,
            "Purple": 0,
            "Gray": 0,
            "White": 0,
        }

        diaries = Diary.query.filter(
            Diary.user_id == user_id,
            extract("year", Diary.date) == year,
            extract("month", Diary.date) == month,
            (
                Diary.date <= current_date
                if year == current_date.year and month == current_date.month
                else True
            ),
        ).all()

        for diary in diaries:
            day = diary.date.day - 1
            diary_list[day] = diary.to_limited_dict()
            if diary.reply_paletter_code != "":
                emotion = diary.reply_paletter_code.split("-")[0]
                if emotion in emotion_counts:
                    emotion_counts[emotion] += 1

        total_count = sum(count for count in emotion_counts.values() if count > 0)
        emotion_percentage = [
            {
                "uid": str(uuid.uuid4()),
                "emotion": emotion,
                "percentage": (
                    round((count / total_count) * 100, 2) if total_count > 0 else 0
                ),
            }
            for emotion, count in emotion_counts.items()
            if count > 0
        ]

        paletter_ranks = [
            {
                "paletter_code": code,
                "paletter_name": paletter_code_table[code],
                "count": emotion_counts[emotion],
            }
            for code, emotion in zip(paletter_code_table.keys(), emotion_counts.keys())
            if emotion_counts[emotion] > 0
        ]

        emotion_percentage.sort(key=lambda x: x["percentage"], reverse=True)
        paletter_ranks.sort(key=lambda x: x["count"], reverse=True)

        return {
            "diary_list": diary_list,
            "emotion_percentage": emotion_percentage,
            "paletter_ranks": paletter_ranks,
        }, 200
