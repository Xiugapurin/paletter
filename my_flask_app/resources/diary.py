from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import Diary

parser = reqparse.RequestParser()
parser.add_argument(
    "diary_date", type=str, required=True, help="Diary date is required"
)
parser.add_argument("diary_title", type=str)
parser.add_argument(
    "diary_content", type=str, required=True, help="Diary content is required"
)
parser.add_argument("media", type=dict, location="json")
parser.add_argument("summary", type=str, required=True, help="Summary is required")
parser.add_argument(
    "summary_embedding",
    type=list,
    location="json",
    required=True,
    help="Summary embedding is required",
)


class DiaryResource(Resource):
    def get(self, user_id, diary_id):
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()

        return diary.to_dict()

    def put(self, user_id, diary_id):
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()
        args = parser.parse_args()
        diary.diary_date = args.get("diary_date", diary.diary_date)
        diary.diary_title = args.get("diary_title", diary.diary_title)
        diary.diary_content = args.get("diary_content", diary.diary_content)
        diary.media = args.get("media", diary.media)
        diary.summary = args.get("summary", diary.summary)
        diary.summary_embedding = args.get("summary_embedding", diary.summary_embedding)
        db.session.commit()

        return diary.to_dict()

    def delete(self, user_id, diary_id):
        diary = Diary.query.filter_by(user_id=user_id, diary_id=diary_id).first_or_404()
        db.session.delete(diary)
        db.session.commit()

        return "", 204


class DiaryListResource(Resource):
    def get(self, user_id):
        diaries = (
            Diary.query.filter_by(user_id=user_id)
            .order_by(Diary.diary_date.desc())
            .all()
        )

        return [diary.to_dict() for diary in diaries]

    def post(self, user_id):
        args = parser.parse_args()
        new_diary = Diary(
            user_id=user_id,
            diary_date=args["diary_date"],
            diary_title=args.get("diary_title"),
            diary_content=args["diary_content"],
            media=args.get("media"),
            summary=args["summary"],
            summary_embedding=args["summary_embedding"],
        )
        db.session.add(new_diary)
        db.session.commit()

        return new_diary.to_dict(), 201
