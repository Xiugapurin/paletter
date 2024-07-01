from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import User, Diary, Message
from my_flask_app.langchain.responses import get_embedding, get_chat_responses

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class MessageListResource(Resource):
    def get(self):
        user_id = g.user_id

        messages = Message.query.filter_by(user_id=user_id).all()
        if not messages:
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

        chat_history_context = ""
        for message in reversed(chat_history):
            sender = "我" if message.sender == "USER" else "精靈"
            chat_history_context += f"{sender}: {message.content}\n"

        content_embedding = get_embedding(content)
        relevant_diaries = (
            Diary.query.filter_by(user_id=user_id)
            .order_by(Diary.summary_embedding.cosine_distance(content_embedding))
            .limit(5)
            .all()
        )

        diary_context = ""
        for i, diary in enumerate(relevant_diaries):
            diary_context += f"線索{str(i+1)} - {diary.date.isoformat()} 的日記內容: {diary.summary}\n"

        print(diary_context)

        user_message = Message(
            user_id=user_id,
            sender="USER",
            content=content,
            emotion="None",
            send_time=datetime.now(),
        )
        db.session.add(user_message)

        ai_response_contents, emotion = get_chat_responses(
            content, llm_preference, chat_history_context, diary_context
        )
        ai_messages = []
        for response in ai_response_contents:
            ai_message = Message(
                user_id=user_id,
                sender="AI",
                emotion=emotion,
                content=response,
                send_time=datetime.now(),
            )
            db.session.add(ai_message)
            ai_messages.append(ai_message)

        db.session.commit()

        return {
            "ai_messages": [msg.to_dict() for msg in ai_messages],
        }, 200
