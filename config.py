import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    SCHEDULER_TIMEZONE = "Asia/Taipei"
    SCHEDULER_API_ENABLED = True
