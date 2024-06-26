from .extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    llm_preference = db.Column(db.String(255))
    profile_picture = db.Column(db.Text)
    created_time = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)

    # diaries = db.relationship(
    #     "Diary", backref="users", lazy=True, cascade="all, delete-orphan"
    # )
    # diaries = db.relationship(
    #     "Diary", backref="users", lazy=True, cascade="all, delete-orphan"
    # )

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "llm_preference": self.llm_preference,
            "profile_picture": self.profile_picture,
            "created_time": self.created_time.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class Diary(db.Model):
    __tablename__ = "diary"

    diary_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String(50),
        db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    diary_date = db.Column(db.Date, nullable=False)
    diary_title = db.Column(db.String(255))
    diary_content = db.Column(db.Text, nullable=False)
    media = db.Column(JSONB)
    has_chat = db.Column(db.Boolean, default=False)
    summary = db.Column(db.Text, nullable=False)
    summary_embedding = db.Column(Vector(1536), nullable=False)

    def to_dict(self):
        return {
            "diary_id": self.diary_id,
            "user_id": self.user_id,
            "diary_date": self.diary_date,
            "diary_title": self.diary_title,
            "diary_content": self.diary_content,
            "media": self.media,
            "has_chat": self.has_chat,
            "summary": self.summary,
            "summary_embedding": self.summary_embedding,
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
    send_time = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            "message_id": self.message_id,
            "user_id": self.user_id,
            "sender": self.sender,
            "content": self.content,
            "send_time": self.send_time,
        }
