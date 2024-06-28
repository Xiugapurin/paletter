from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import User, Message
from my_flask_app.langchain.responses import get_chat_responses

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class MessageListResource(Resource):
    def get(self):
        user_id = g.user_id

        messages = Message.query.filter_by(user_id=user_id).all()
        if not messages:
            # 沒有訊息時，回傳提示訊息
            ai_message = {
                "message_id": "initial_message",
                "user_id": user_id,
                "sender": "AI",
                "content": "有什麼煩惱要跟我說說嗎？",
                "send_time": datetime.now().isoformat(),
            }
            return {"messages": [ai_message]}, 200

        return {"messages": [message.to_dict() for message in messages]}, 200

    def post(self):
        args = parser.parse_args()
        content = args["content"]
        user_id = g.user_id

        user = User.query.get_or_404(user_id)
        llm_preference = user.llm_preference

        chat_history = (
            Message.query.filter_by(user_id=user_id)
            .order_by(Message.send_time.desc())
            .limit(10)
            .all()
        )

        context = ""
        for message in reversed(chat_history):
            sender = "使用者" if message.sender == "USER" else "精靈"
            context += f"{sender}: {message.content}\n"

        user_message = Message(
            user_id=user_id, sender="USER", content=content, send_time=datetime.now()
        )
        db.session.add(user_message)

        ai_response_contents = get_chat_responses(content, llm_preference, context)
        ai_messages = []
        for response in ai_response_contents:
            ai_message = Message(
                user_id=user_id,
                sender="AI",
                content=response,
                send_time=datetime.now(),
            )
            db.session.add(ai_message)
            ai_messages.append(ai_message)

        db.session.commit()

        return {
            "ai_messages": [msg.to_dict() for msg in ai_messages],
        }, 200
