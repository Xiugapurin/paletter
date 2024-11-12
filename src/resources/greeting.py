from datetime import datetime, timedelta
from flask import g
from flask_restful import Resource, reqparse
from src.models import User, Paletter, Diary, DiaryEntry, Message
from src.langchain.responses import get_greeting

parser = reqparse.RequestParser()


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
                    "sender": "喵喵",
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


class GreetingResource(Resource):
    def get(self):
        user_id = g.user_id
        today = datetime.now().date()

        user = User.query.get_or_404(user_id)
        user_name = user.name
        days = str((datetime.now() - user.created_time).days + 1)

        days_ago = today - timedelta(days=2)
        diaries = Diary.query.filter(
            Diary.user_id == user_id, Diary.date >= days_ago, Diary.date <= today
        ).all()

        start_date = datetime.combine(days_ago, datetime.min.time())
        end_date = datetime.combine(today, datetime.max.time())

        all_entries = []
        diary_ids = [diary.diary_id for diary in diaries]

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
                Message.send_time >= start_date,
                Message.send_time <= end_date,
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

        greeting = get_greeting(
            user_name, days, diary_contents_str, message_contents_str
        )

        return {
            "greeting": greeting,
        }, 200
