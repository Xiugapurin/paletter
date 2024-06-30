import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    SCHEDULER_TIMEZONE = "Asia/Taipei"
    SCHEDULER_API_ENABLED = True
