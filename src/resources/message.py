from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import User, Diary, Message
from src.langchain.responses import (
    get_embedding,
    get_chat_responses,
)

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class MessageResource(Resource):
    def get(self):
        pass

    def delete(self):
        user_id = g.user_id
        pass


class MessageListResource(Resource):
    def get(self, page):
        user_id = g.user_id

        try:
            page = int(page)
        except ValueError:
            return {"error": "Invalid page format."}, 400

        if page < 1:
            return {"error": "Page number must be greater than or equal to 1."}, 400

        pagination = (
            Message.query.filter_by(user_id=user_id)
            .order_by(Message.message_id)
            .paginate(page=page, per_page=50, error_out=False)
        )

        if not pagination.items:
            ai_message = {
                "message_id": "initial_message",
                "user_id": user_id,
                "sender": "AI",
                "content": "有什麼煩惱要跟我說說嗎？",
                "send_time": datetime.now().isoformat(),
            }
            return {"messages": [ai_message]}, 200

        messages = [message.to_dict() for message in pagination.items]
        next_page = pagination.page + 1 if pagination.has_next else -1

        return {
            "messages": messages,
            "next_page": next_page,
            "total_pages": pagination.pages,
        }, 200


class MessageResponseResource(Resource):
    def post(self):
        args = parser.parse_args()
        content = args["content"]
        user_id = g.user_id

        user = User.query.get_or_404(user_id)
        llm_preference = user.llm_preference
        user_name = user.name
        membership_level = user.membership_level

        relevant_diary_context = ""
        if membership_level == "Premium" or membership_level == "VIP":
            content_embedding = get_embedding(content)
            relevant_diaries = (
                Diary.query.filter_by(user_id=user_id)
                .order_by(Diary.summary_embedding.cosine_distance(content_embedding))
                .limit(5)
                .all()
            )

            for i, diary in enumerate(relevant_diaries):
                relevant_diary_context += f"線索{str(i+1)} - {diary.date.isoformat()} 的日記內容: {diary.summary}\n"

        chat_history = (
            Message.query.filter_by(user_id=user_id)
            .order_by(Message.send_time.desc())
            .limit(10)
            .all()
        )
        chat_history_context = ""
        for message in reversed(chat_history):
            sender = "朋友" if message.sender == "USER" else "波波"
            chat_history_context += f"{sender}: {message.content}\n"

        today = datetime.now().date()
        today_diary = Diary.query.filter_by(user_id=user_id, date=today).first()
        today_diary_context = "今天沒有日記"
        if today_diary:
            today_diary_context = today_diary.content

        user_message = Message(
            user_id=user_id,
            sender="USER",
            content=content,
            send_time=datetime.now(),
        )
        db.session.add(user_message)

        ai_response_contents, emotion = get_chat_responses(
            content,
            user_name,
            llm_preference,
            chat_history_context,
            relevant_diary_context,
            today_diary_context,
            membership_level,
        )

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

        # TODO: add emotion
        return {
            "ai_messages": [msg.to_dict() for msg in ai_messages],
            "emotion": emotion,
        }, 200
