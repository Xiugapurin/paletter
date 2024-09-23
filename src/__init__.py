import os
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api
import firebase_admin
from firebase_admin import credentials, auth
from config import Config
from .extensions import db, migrate, scheduler
from .tasks import paint_daily_diary, refresh_daily_diary
from src.resources.user import UserResource, UserListResource
from src.resources.diary import DiaryResource, DiaryListResource
from src.resources.message import MessageListResource, MessageResponseResource
from src.resources.color import ColorResource, ColorListResource


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.logger.setLevel(logging.DEBUG)

    gunicorn_error_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_error_logger.handlers
    app.logger.setLevel(gunicorn_error_logger.level)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)

    scheduler.init_app(app)
    # scheduler.add_job(
    #     func=paint_daily_diary, trigger="cron", hour=14, minute=52, id="daily_paint"
    # )
    # scheduler.add_job(
    #     func=refresh_daily_diary, trigger="cron", hour=6, minute=0, id="daily_refresh"
    # )
    scheduler.start()

    cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)

    api = Api(app)
    api.add_resource(UserResource, "/api/user")
    api.add_resource(UserListResource, "/api/users")
    api.add_resource(DiaryResource, "/api/diary/<int:diary_id>")
    api.add_resource(DiaryListResource, "/api/diaries/<int:page>")
    api.add_resource(ColorResource, "/api/color/<string:color>")
    api.add_resource(ColorListResource, "/api/colors/<int:year>/<int:month>")
    api.add_resource(MessageListResource, "/api/messages/<int:page>")
    api.add_resource(MessageResponseResource, "/api/messages")

    @app.before_request
    def authenticate_user():
        try:
            if request.method != "OPTIONS":
                auth_header = request.headers.get("Authorization")

                if not auth_header:
                    return jsonify({"error": "Unauthorized"}), 401

                bearer_token = auth_header.split(" ")[1]
                decoded_token = auth.verify_id_token(bearer_token)
                g.user_id = decoded_token["uid"]
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    return app
