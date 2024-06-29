from datetime import datetime, timedelta
from calendar import monthrange
from flask import g
from flask_restful import Resource, reqparse
from sqlalchemy import extract
from my_flask_app import db
from my_flask_app.models import Diary

parser = reqparse.RequestParser()


class DiaryResource(Resource):
    def get(self, diary_id):
        user_id = g.user_id
        if diary_id == 0:
            today = datetime.now() + timedelta(hours=8)
            today_date = today.date()

            diary = Diary.query.filter_by(user_id=user_id, date=today_date).first()

            if not diary:
                print("Creating new diary")
                diary = Diary(
                    user_id=user_id, date=today_date, status="EDITING", summary=""
                )
                db.session.add(diary)
                db.session.commit()

            return diary.to_dict(), 200

        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        return diary.to_dict(), 200

    def put(self, diary_id):
        user_id = g.user_id
        parser.add_argument("content", type=str, required=True, help="Diary content")
        parser.add_argument("media", type=dict, required=False, help="Diary media")
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        args = parser.parse_args()
        diary.content = args.get("content")
        diary.media = args.get("media", diary.media)
        db.session.commit()

        return diary.to_dict()

    def delete(self, diary_id):
        user_id = g.user_id
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        db.session.delete(diary)
        db.session.commit()

        return "", 200


class DiaryListResource(Resource):
    def get(self):
        user_id = g.user_id
        parser.add_argument(
            "page", type=int, required=False, default=1, help="Page number"
        )
        args = parser.parse_args()
        page = args.get("page", 1)

        pagination = (
            Diary.query.filter_by(user_id=user_id)
            .order_by(Diary.date.desc())
            .paginate(page, 20, error_out=False)
        )

        diaries = [diary.to_limited_dict() for diary in pagination.items]
        return {
            "diaries": diaries,
            "current_page": pagination.page,
        }, 200

    def post(self):
        user_id = g.user_id

        new_diary = Diary(
            user_id=user_id,
            media={},
        )
        db.session.add(new_diary)
        db.session.commit()

        return new_diary.to_dict(), 200


class DiaryCalenderResource(Resource):
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
        diary_list = [{"diary_id": -1, "color": "GRAY"} for _ in range(days_in_month)]

        diaries = Diary.query.filter(
            Diary.user_id == user_id,
            extract("year", Diary.date) == year,
            extract("month", Diary.date) == month,
        ).all()

        for diary in diaries:
            day = diary.date.day
            diary_list[day - 1] = {"diary_id": diary.diary_id, "color": diary.color}

        return diary_list, 200
