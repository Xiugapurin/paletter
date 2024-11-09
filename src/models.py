from datetime import datetime, date
from sqlalchemy.orm import validates
from pgvector.sqlalchemy import Vector
from .extensions import db
from src.constants.paletter_table import paletter_name_table


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.Text)
    membership_level = db.Column(db.String(15), default="Basic", nullable=False)
    credit_limit = db.Column(db.Integer, default=0, nullable=False)
    is_trial = db.Column(db.Boolean, default=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_login_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # def to_dict(self):
    #     return {
    #         "name": self.name,
    #         "profile_picture": self.profile_picture,
    #         "membership_level": self.membership_level,
    #         "credit_limit": self.credit_limit,
    #         "is_trial": self.is_trial,
    #     }

    def to_dict(self):
        return {"name": self.name, "profile_picture": self.profile_picture}


class Diary(db.Model):
    __tablename__ = "diaries"

    diary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    date = db.Column(db.Date, default=date.today, nullable=False)
    reply_paletter_code = db.Column(db.String(31), default="", nullable=False)
    reply_content = db.Column(db.Text, default="", nullable=False)
    reply_picture = db.Column(db.Text, default="", nullable=False)

    def to_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "reply_paletter_code": self.reply_paletter_code,
            "reply_content": self.reply_content,
        }

    def to_limited_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "emotion": self.reply_paletter_code.split("-")[0],
            "reply_paletter_code": self.reply_paletter_code,
        }

    def to_emotion_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "emotion": self.reply_paletter_code.split("-")[0],
            "paletter_code": self.reply_paletter_code,
        }


class DiaryEntry(db.Model):
    __tablename__ = "diary_entries"

    diary_entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diary_id = db.Column(
        db.Integer,
        db.ForeignKey("diaries.diary_id", ondelete="CASCADE"),
        nullable=False,
    )
    title = db.Column(db.String(63), default="", nullable=False)
    content = db.Column(db.Text, default="", nullable=False)
    emotion = db.Column(db.String(15), default="", nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_edit_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            "diary_entry_id": self.diary_entry_id,
            "title": self.title,
            "content": self.content,
            "emotion": self.emotion,
            "created_time": self.created_time.isoformat(),
            "last_edit_time": self.last_edit_time.isoformat(),
        }


class Paletter(db.Model):
    __tablename__ = "paletters"

    paletter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    paletter_code = db.Column(db.String(31), nullable=False)
    intimacy_level = db.Column(db.Integer, default=0, nullable=False)
    vitality_value = db.Column(db.Integer, default=500, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_chat_time = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @validates("intimacy_level", "vitality_value")
    def validate_range(self, key, value):
        if key == "intimacy_level" and (value < 0 or value > 100):
            raise ValueError("intimacy_level must between 0 to 100.")
        if key == "vitality_value" and (value < 0 or value > 500):
            raise ValueError("vitality_value must between 0 to 500.")
        return value

    def to_dict(self):
        return {
            "paletter_id": self.paletter_id,
            "paletter_code": self.paletter_code,
            "paletter_name": paletter_name_table[self.paletter_code],
            "intimacy_level": self.intimacy_level,
            "vitality_value": self.vitality_value,
            "created_time": self.created_time.isoformat(),
            "last_chat_time": self.last_chat_time.isoformat(),
        }


class Message(db.Model):
    __tablename__ = "messages"

    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    paletter_id = db.Column(
        db.Integer,
        db.ForeignKey("paletters.paletter_id", ondelete="CASCADE"),
        nullable=False,
    )
    sender = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "content": self.content,
            "send_time": self.send_time.isoformat(),
        }


class Knowledge(db.Model):
    __tablename__ = "knowledge"

    knowledge_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    paletter_id = db.Column(
        db.Integer,
        db.ForeignKey("paletters.paletter_id", ondelete="CASCADE"),
        nullable=False,
    )
    source = db.Column(db.String(15), nullable=False)
    source_id = db.Column(db.Integer, default=-1, nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    content = db.Column(db.Text, nullable=False)
    embedding = db.Column(Vector(1536))
    activate_count = db.Column(db.Integer, default=0, nullable=False)
    is_activate = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            "knowledge_id": self.knowledge_id,
            "user_id": self.user_id,
            "paletter_id": self.paletter_id,
            "diary_id": self.diary_id,
            "type": self.type,
            "date": self.date.isoformat(),
            "content": self.content,
            "embedding": self.embedding,
            "activate_count": self.activate_count,
            "is_activate": self.is_activate,
        }
