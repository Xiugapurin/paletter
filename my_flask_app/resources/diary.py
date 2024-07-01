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
            today = datetime.now()
            today_date = today.date()

            diary = Diary.query.filter_by(user_id=user_id, date=today_date).first()

            if not diary:
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

        diaries = [diary.to_limited_dict() for diary in pagination.items]
        next_page = pagination.page + 1 if pagination.has_next else -1

        return {
            "diaries": diaries,
            "next_page": next_page,
            "total_pages": pagination.pages,
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
