from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import Diary, DiaryEntry
from src.langchain.responses import get_diary_emotion

parser = reqparse.RequestParser()


class DiaryEntryResource(Resource):
    def put(self, diary_id, diary_entry_id):
        user_id = g.user_id
        parser.add_argument("title", type=str, required=False, help="Diary entry title")
        parser.add_argument(
            "content", type=str, required=True, help="Diary entry content"
        )

        if diary_id == 0:
            today = datetime.now().date()
            diary = Diary.query.filter_by(user_id=user_id, date=today).first()

            if not diary:
                return {"message": "Diary not found"}, 404

            diary_id = diary.diary_id

        diary = Diary.query.filter_by(diary_id=diary_id, user_id=user_id).first()
        if not diary:
            return {"message": "Diary not found or does not belong to the user"}, 404

        args = parser.parse_args()
        title = args.get("title", "心情小記")
        content = args["content"]
        emotion = get_diary_emotion(content)

        # Create new entry
        if diary_entry_id == 0:

            new_diary_entry = DiaryEntry(
                diary_id=diary_id,
                title=title,
                content=content,
                emotion=emotion,
            )
            db.session.add(new_diary_entry)
            db.session.commit()

            return new_diary_entry.to_dict(), 200

        # Update existing entry
        diary_entry = DiaryEntry.query.filter_by(
            diary_id=diary_id, diary_entry_id=diary_entry_id
        ).first_or_404()

        diary_entry.title = title
        diary_entry.content = content
        diary_entry.emotion = emotion
        diary_entry.last_edit_time = datetime.now()

        db.session.commit()

        return diary_entry.to_dict(), 200

    def delete(self, diary_id, diary_entry_id):
        user_id = g.user_id
        diary = Diary.query.filter_by(diary_id=diary_id, user_id=user_id).first()
        if not diary:
            return {"message": "Diary not found or does not belong to the user"}, 404

        diary_entry = DiaryEntry.query.filter_by(
            diary_id=diary_id, diary_entry_id=diary_entry_id
        ).first_or_404()

        db.session.delete(diary_entry)
        db.session.commit()

        return {"message": "Diary entry deleted"}, 200


class DiaryEntryListResource(Resource):
    def get(self, diary_id):
        user_id = g.user_id

        if diary_id == 0:
            today = datetime.now().date()

            diary = Diary.query.filter_by(user_id=user_id, date=today).first()

            if not diary:
                return {"message": "Diary not found"}, 404

            diary_id = diary.diary_id

        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first()
        if not diary:
            return {"message": "Diary not found or does not belong to the user"}, 404

        diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

        if not diary_entries:
            return {"diary_entries": []}, 200

        return {
            "diary_entries": [entry.to_dict() for entry in diary_entries],
        }, 200

    def post(self, diary_id):
        user_id = g.user_id
        parser.add_argument("title", type=str, required=False, help="Diary entry title")
        parser.add_argument(
            "content", type=str, required=True, help="Diary entry content"
        )

        if diary_id == 0:
            today = datetime.now().date()

            diary = Diary.query.filter_by(user_id=user_id, date=today).first()

            if not diary:
                return {"message": "Diary not found"}, 404

            diary_id = diary.diary_id

        diary = Diary.query.filter_by(diary_id=diary_id, user_id=user_id).first()
        if not diary:
            return {"message": "Diary not found or does not belong to the user"}, 404

        args = parser.parse_args()
        title = args.get("title", "心情小記")
        content = args.get("content")
        emotion = get_diary_emotion(content)

        new_diary_entry = DiaryEntry(
            diary_id=diary_id, title=title, content=content, emotion=emotion
        )

        db.session.add(new_diary_entry)
        db.session.commit()

        return new_diary_entry.to_dict(), 200
