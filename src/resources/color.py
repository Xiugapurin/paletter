from datetime import datetime
from calendar import monthrange
from flask import g
from flask_restful import Resource
from sqlalchemy import extract
from src.models import Diary, Color


class ColorResource(Resource):
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


class ColorListResource(Resource):
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

        diary_list = [{"diary_id": -1, "colors": ["White"]}] * (days_in_month)
        color_counts = {
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
            day = diary.date.day
            colors = Color.query.filter_by(diary_id=diary.diary_id).all()
            colors_list = [c.color for c in colors]
            if colors_list:
                diary_list[day - 1] = {
                    "diary_id": diary.diary_id,
                    "colors": colors_list,
                }
                for color in colors_list:
                    color_counts[color] += 1

        total_colors = sum(color_counts.values())
        if total_colors > 0:
            color_percentages = {
                color: round((count / total_colors) * 100, 1)
                for color, count in color_counts.items()
            }
        else:
            color_percentages = {color: 0 for color in color_counts}

        return {"diary_list": diary_list, "color_percentages": color_percentages}, 200
