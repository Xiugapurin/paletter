from datetime import datetime, date
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    llm_preference = db.Column(db.String(255))
    profile_picture = db.Column(db.Text)
    membership_level = db.Column(db.String(15), default="Basic", nullable=False)
    credit_limit = db.Column(db.Integer, default=0, nullable=False)
    has_completed_diary = db.Column(db.Boolean, default=False, nullable=False)
    is_trial = db.Column(db.Boolean, default=True, nullable=False)
    created_time = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    last_login = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "llm_preference": self.llm_preference,
            "profile_picture": self.profile_picture,
            "membership_level": self.membership_level,
            "credit_limit": self.credit_limit,
            "has_completed_diary": self.has_completed_diary,
            "is_trial": self.is_trial,
        }


class Diary(db.Model):
    __tablename__ = "diaries"

    diary_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    date = db.Column(db.Date, default=date.today, nullable=False)
    content = db.Column(db.Text, default="", nullable=False)
    media = db.Column(JSONB)
    status = db.Column(db.String(15), nullable=False)
    type = db.Column(db.String(15), default="")
    summary = db.Column(db.String(255), default="")
    tag = db.Column(db.String(63), default="")

    def to_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "content": self.content,
            "status": self.status,
            "type": self.type,
            "summary": self.summary,
            "tag": self.tag,
        }

    def to_limited_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "status": self.status,
        }


class Color(db.Model):
    __tablename__ = "colors"

    color_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    diary_id = db.Column(
        db.Integer,
        db.ForeignKey("diaries.diary_id", ondelete="CASCADE"),
        nullable=False,
    )
    color = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(20))
    content = db.Column(db.Text, default="", nullable=False)

    def to_dict(self):
        return {
            "color_id": self.color_id,
            "diary_id": self.diary_id,
            "color": self.color,
            "type": self.type,
            "content": self.content,
        }


class Message(db.Model):
    __tablename__ = "messages"

    message_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
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
    date = db.Column(db.Date, default=date.today, nullable=False)
    owner = db.Column(db.String(15), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_activate = db.Column(db.Boolean, default=True, nullable=False)
    embedding = db.Column(Vector(1536))

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "diary_id": self.diary_id,
            "chunk_content": self.chunk_content,
        }