from datetime import datetime, timedelta
from flask import g
from flask_restful import Resource, reqparse
from src import db
from src.models import User, Paletter, Diary, DiaryEntry, Message, Knowledge
from src.langchain.responses import get_chat_responses, get_weekly_report
from src.langchain.utils import get_embedding
from src.constants.paletter_table import paletter_name_table

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


def merge_consecutive_ai_messages(message_contents):
    merged_messages = []
    temp_ai_message = None

    for message in message_contents:
        current_time = message["send_time"]
        sender = message["sender"]
        content = message["content"]

        if sender == "AI":
            if temp_ai_message is None:
                temp_ai_message = {
                    "send_time": current_time,
                    "sender": "AI",
                    "content": content,
                }
            else:
                temp_ai_message["content"] += " " + content
        else:
            if temp_ai_message is not None:
                merged_messages.append(temp_ai_message)
                temp_ai_message = None

            merged_messages.append(
                {"send_time": current_time, "sender": sender, "content": content}
            )

    if temp_ai_message is not None:
        merged_messages.append(temp_ai_message)

    formatted_messages = []
    for message in merged_messages:
        formatted_message = (
            f"Time: {message['send_time'].strftime('%m-%d %H:%M')}\n"
            f"Sender: {message['sender']}\n"
            f"Content: {message['content']}"
        )
        formatted_messages.append(formatted_message)

    return "\n---\n".join(formatted_messages)


class MessageResource(Resource):
    def get(self):
        user_id = g.user_id
        today = datetime.now().date()

        user = User.query.get_or_404(user_id)
        user_name = user.name
        days = str((datetime.now() - user.created_time).days + 1)

        week_ago = today - timedelta(days=7)
        weekly_diaries = Diary.query.filter(
            Diary.user_id == user_id, Diary.date >= week_ago, Diary.date <= today
        ).all()

        start_of_week = datetime.combine(week_ago, datetime.min.time())
        end_of_today = datetime.combine(today, datetime.max.time())

        all_entries = []
        diary_ids = [diary.diary_id for diary in weekly_diaries]

        if diary_ids:
            all_entries = (
                DiaryEntry.query.filter(DiaryEntry.diary_id.in_(diary_ids))
                .order_by(DiaryEntry.created_time)
                .all()
            )

        entry_contents = []
        for entry in all_entries:
            entry_contents.append(
                {"content": entry.content, "created_time": entry.created_time}
            )

        messages = (
            Message.query.join(Paletter, Message.paletter_id == Paletter.paletter_id)
            .filter(
                Message.user_id == user_id,
                Paletter.paletter_code == "Pal-1",
                Message.send_time >= start_of_week,
                Message.send_time <= end_of_today,
            )
            .order_by(Message.send_time)
            .all()
        )

        message_contents = []
        for message in messages:
            message_contents.append(
                {
                    "content": message.content,
                    "sender": message.sender,
                    "send_time": message.send_time,
                }
            )

        formatted_entries = []
        for entry in entry_contents:
            formatted_entry = (
                f"Time: {entry['created_time'].strftime('%m-%d %H:%M')}\n"
                f"Content: {entry['content']}"
            )
            formatted_entries.append(formatted_entry)
        diary_contents_str = "\n---\n".join(formatted_entries)
        message_contents_str = merge_consecutive_ai_messages(message_contents)

        weekly_report = get_weekly_report(
            user_name, days, diary_contents_str, message_contents_str
        )

        return {
            "report_start_date": week_ago.strftime("%Y-%m-%d"),
            "report_end_date": today.strftime("%Y-%m-%d"),
            "report_content": weekly_report,
        }, 200


class MessageListResource(Resource):
    def get(self, paletter_id, page):
        user_id = g.user_id

        paletter = Paletter.query.get_or_404(paletter_id)
        paletter_name = paletter_name_table.get(paletter.paletter_code, "Unknown")

        try:
            page = int(page)
        except ValueError:
            return {"error": "Invalid page format."}, 400

        if page < 1:
            return {"error": "Page number must be greater than or equal to 1."}, 400

        pagination = (
            Message.query.filter_by(user_id=user_id, paletter_id=paletter_id)
            .order_by(Message.message_id.desc())
            .paginate(page=page, per_page=50, error_out=False)
        )

        if not pagination.items:
            ai_message = {
                "message_id": -1,
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

        messages = [message.to_dict() for message in pagination.items][::-1]
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
        paletter_name = paletter_name_table[paletter_code]
        days = str((datetime.now() - paletter.created_time).days + 1)

        relevant_context = ""
        if membership_level == "Premium" or membership_level == "VIP":
            content_embedding = get_embedding(content)
            relevant_knowledge = (
                Knowledge.query.filter_by(user_id=user_id, paletter_id=paletter_id)
                .order_by(Knowledge.embedding.cosine_distance(content_embedding))
                .limit(8)
                .all()
            )

            for i, knowledge in enumerate(relevant_knowledge):
                context_source = "日記" if knowledge.source == "Diary" else "訊息"
                relevant_context += (
                    f"線索{str(i+1)} - {context_source}內容: {knowledge.content}\n---\n"
                )

        chat_history = (
            Message.query.filter_by(user_id=user_id, paletter_id=paletter_id)
            .order_by(Message.send_time.desc())
            .limit(20)
            .all()
        )
        chat_history_context = ""
        chat_history_context_clue = ""
        for message in reversed(chat_history):
            if message.sender == "USER":
                sender = clue_sender = "朋友"
            elif message.sender == "AI":
                sender = paletter_name
                clue_sender = f"{paletter_name} (AI)"
            chat_history_context += f"{sender}: {message.content}\n"
            chat_history_context_clue += f"{clue_sender}: {message.content}\n"

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

        ai_response_contents = get_chat_responses(
            content,
            user_name,
            paletter_code,
            paletter_name,
            days,
            chat_history_context,
            chat_history_context_clue,
            relevant_context,
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

        return {
            "ai_messages": [msg.to_dict() for msg in ai_messages],
        }, 200
