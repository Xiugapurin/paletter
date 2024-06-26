import os
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth
from config import Config
from .extensions import db, migrate
from flask_restful import Api
from my_flask_app.resources.user import UserResource, UserListResource
from my_flask_app.resources.diary import DiaryResource, DiaryListResource
from my_flask_app.resources.message import MessageListResource


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    cred = credentials.Certificate(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
    firebase_admin.initialize_app(cred)

    api = Api(app)
    api.add_resource(UserResource, "/api/user")
    api.add_resource(UserListResource, "/api/users")
    api.add_resource(DiaryResource, "/api/diary/<int:diary_id>")
    api.add_resource(DiaryListResource, "/api/diaries")
    api.add_resource(MessageListResource, "/api/messages")

    @app.before_request
    def authenticate_user():
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "未提供授權標頭"}), 401

        try:
            bearer_token = auth_header.split(" ")[1]
            decoded_token = auth.verify_id_token(bearer_token)
            request.user_id = decoded_token["uid"]
        except Exception as e:
            return jsonify({"error": str(e)}), 401

    return app
