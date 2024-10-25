from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import Paletter

parser = reqparse.RequestParser()


# class DiaryResource(Resource):
#     def get(self, diary_id):
#         user_id = g.user_id

#         # Today's diary
#         if diary_id == 0:
#             today = datetime.now().date()

#             diary = Diary.query.filter_by(user_id=user_id, date=today).first()

#             if not diary:
#                 diary = Diary(user_id=user_id)
#                 db.session.add(diary)
#                 db.session.commit()

#                 return {
#                     "diary_info": diary.to_dict(),
#                     "diary_entries": [],
#                 }, 200

#             diary_id = diary.diary_id
#         else:
#             diary = Diary.query.filter_by(
#                 user_id=user_id, diary_id=diary_id
#             ).first_or_404()

#         diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

#         return {
#             "diary_info": diary.to_dict(),
#             "diary_entries": [entry.to_dict() for entry in diary_entries],
#         }, 200

#     def put(self, diary_id):
#         user_id = g.user_id

#         diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

#         db.session.commit()

#         return diary.to_dict(), 200

#     def delete(self, diary_id):
#         user_id = g.user_id
#         diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

#         db.session.delete(diary)
#         db.session.commit()

#         return "", 200


class PaletterListResource(Resource):
    def get(self):
        user_id = g.user_id

        paletters = Paletter.query.filter_by(user_id=user_id).all()

        return {
            "paletters": [p.to_dict() for p in paletters],
        }, 200
