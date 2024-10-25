from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import User, Paletter, Diary, DiaryEntry, Message
from src.langchain.responses import (
    get_embedding,
    get_chat_responses,
)
from src.constant.paletter_table import paletter_code_table

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class MessageResource(Resource):
    def get(self):
        pass

    def delete(self):
        user_id = g.user_id
        pass


class MessageListResource(Resource):
    def get(self, paletter_id, page):
        user_id = g.user_id

        paletter = Paletter.query.get_or_404(paletter_id)
        paletter_name = paletter_code_table.get(paletter.paletter_code, "Unknown")

        try:
            page = int(page)
        except ValueError:
            return {"error": "Invalid page format."}, 400

        if page < 1:
            return {"error": "Page number must be greater than or equal to 1."}, 400

        pagination = (
            Message.query.filter_by(user_id=user_id, paletter_id=paletter_id)
            .order_by(Message.message_id)
            .paginate(page=page, per_page=50, error_out=False)
        )

        if not pagination.items:
            ai_message = {
                "message_id": "initial_message",
                "user_id": user_id,
                "paletter_id": paletter_id,
                "sender": "AI",
                "content": "有什麼煩惱要跟我說說嗎？",
                "send_time": datetime.now().isoformat(),
            }

            return {
                "paletter_name": paletter_name,
                "messages": [ai_message],
                "next_page": -1,
                "total_pages": 1,
            }, 200

        messages = [message.to_dict() for message in pagination.items]
        next_page = pagination.page + 1 if pagination.has_next else -1

        return {
            "paletter_name": paletter_name,
            "messages": messages,
            "next_page": next_page,
            "total_pages": pagination.pages,
        }, 200


class MessageResponseResource(Resource):
    def post(self, paletter_id):
        args = parser.parse_args()
        content = args["content"]
        user_id = g.user_id

        user = User.query.get_or_404(user_id)
        paletter = Paletter.query.get_or_404(paletter_id)

        user_name = user.name
        membership_level = user.membership_level

        paletter_code = paletter.paletter_code
        paletter_name = paletter_code_table[paletter_code]
        days = str((datetime.now() - paletter.created_time).days + 1)

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
            Message.query.filter_by(user_id=user_id, paletter_id=paletter_id)
            .order_by(Message.send_time.desc())
            .limit(12)
            .all()
        )
        chat_history_context = ""
        for message in reversed(chat_history):
            if message.sender == "USER":
                sender = "朋友"
            elif message.sender == "AI":
                sender = paletter_name
            chat_history_context += f"{sender}: {message.content}\n"

        today = datetime.now().date()
        today_diary = Diary.query.filter_by(user_id=user_id, date=today).first()
        today_diary_context = "今天沒有日記"
        if today_diary:
            diary_id = today_diary.diary_id
            diary_entries = DiaryEntry.query.filter_by(diary_id=diary_id).all()

            if diary_entries:
                combined_content = "\n\n".join(
                    [
                        f"{entry.created_time.strftime('%H:%M')} - {entry.content}"
                        for entry in diary_entries
                    ]
                )
                today_diary_context = combined_content

        user_message = Message(
            user_id=user_id,
            paletter_id=paletter_id,
            sender="USER",
            content=content,
            send_time=datetime.now(),
        )
        db.session.add(user_message)

        ai_response_contents, emotion = get_chat_responses(
            content,
            user_name,
            paletter_code,
            paletter_name,
            days,
            chat_history_context,
            relevant_diary_context,
            today_diary_context,
            membership_level,
        )

        ai_messages = []
        for response in ai_response_contents:
            ai_message = Message(
                user_id=user_id,
                paletter_id=paletter_id,
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
