import os
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_restful import Api
import firebase_admin
from firebase_admin import credentials, auth
from config import Config
from .extensions import db, migrate
from src.resources.user import UserResource
from src.resources.paletter import PaletterListResource
from src.resources.greeting import GreetingResource
from src.resources.diary import DiaryResource, DiaryListResource
from src.resources.diary_entry import DiaryEntryResource, DiaryEntryListResource
from src.resources.message import (
    MessageResource,
    MessageListResource,
    MessageResponseResource,
)
from src.resources.emotion import EmotionListResource


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

    cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)
    # firebase_admin.initialize_app()

    api = Api(app)
    api.add_resource(UserResource, "/api/user")
    api.add_resource(PaletterListResource, "/api/paletters")
    api.add_resource(GreetingResource, "/api/greeting")
    api.add_resource(DiaryResource, "/api/diary/<int:diary_id>")
    api.add_resource(DiaryListResource, "/api/diaries/<int:page>")
    api.add_resource(
        DiaryEntryResource, "/api/diary-entry/<int:diary_id>/<int:diary_entry_id>"
    )
    api.add_resource(DiaryEntryListResource, "/api/diary-entries/<int:diary_id>")
    api.add_resource(MessageResource, "/api/message")
    api.add_resource(MessageListResource, "/api/messages/<int:paletter_id>/<int:page>")
    api.add_resource(MessageResponseResource, "/api/messages/<int:paletter_id>")
    api.add_resource(EmotionListResource, "/api/emotions/<int:year>/<int:month>")

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
