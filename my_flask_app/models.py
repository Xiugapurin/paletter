from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from .extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    llm_preference = db.Column(db.String(255))
    profile_picture = db.Column(db.Text)
    created_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "name": self.name,
            "llm_preference": self.llm_preference,
            "profile_picture": self.profile_picture,
            # "created_time": self.created_time.isoformat(),
            # "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class Diary(db.Model):
    __tablename__ = "diaries"

    diary_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    date = db.Column(
        db.Date,
        nullable=False,
        default=datetime.now().date(),
    )
    content = db.Column(db.Text, nullable=False, default="")
    media = db.Column(JSONB)
    status = db.Column(db.String(20), nullable=False, default="EMPTY")
    tag = db.Column(db.String(255))
    summary = db.Column(db.Text, nullable=False, default="")
    summary_embedding = db.Column(Vector(1536))

    def to_dict(self):
        return {
            "diary_id": self.diary_id,
            "date": self.date.isoformat(),
            "content": self.content,
            "status": self.status,
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
    content = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "color_id": self.color_id,
            "diary_id": self.diary_id,
            "color": self.color,
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
    emotion = db.Column(db.String(20), nullable=False, default="")
    content = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "emotion": self.emotion,
            "content": self.content,
            "send_time": self.send_time.isoformat(),
        }
