from flask_restful import Resource, reqparse
from my_flask_app import db
from models import Diary, Message

parser = reqparse.RequestParser()
parser.add_argument(
    "content", type=str, required=True, help="Message content is required"
)


class MessageListResource(Resource):
    def get(self, diary_id):
        messages = (
            Message.query.filter_by(diary_id=diary_id)
            .order_by(Message.send_time.desc())
            .all()
        )

        return [message.to_dict() for message in messages]

    def post(self, diary_id):
        diary = Diary.query.get_or_404(diary_id)
        args = parser.parse_args()
        new_message = Message(diary_id=diary_id, sender="USER", content=args["content"])
        db.session.add(new_message)
        diary.has_chat = True
        db.session.commit()

        return new_message.to_dict(), 201
