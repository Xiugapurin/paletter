from datetime import datetime
from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import Message

parser = reqparse.RequestParser()
parser.add_argument("user_id", type=str, required=True, help="User ID is required")
parser.add_argument("content", type=str)


class MessageListResource(Resource):
    def get(self):
        args = parser.parse_args()
        user_id = args["user_id"]

        messages = Message.query.filter_by(user_id=user_id).all()
        if not messages:
            return {"message": "No messages found for the given user_id"}, 404

        return {"messages": [message.to_dict() for message in messages]}, 200

    def post(self):
        args = parser.parse_args()
        user_id = args["user_id"]
        content = args["content"]
        sender = "USER"

        new_message = Message(
            user_id=user_id, sender=sender, content=content, send_time=datetime.now()
        )

        db.session.add(new_message)
        db.session.commit()

        return {"message": "Message added successfully"}, 200
