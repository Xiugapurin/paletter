from flask import Flask
from config import Config
from .extensions import db, migrate
from flask_restful import Api
from google.oauth2 import id_token
from google.auth.transport import requests
from my_flask_app.resources.user import UserResource, UserListResource
from my_flask_app.resources.diary import DiaryResource, DiaryListResource
from my_flask_app.resources.message import MessageListResource


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.add_resource(UserResource, "/api/user/<string:user_id>")
    api.add_resource(UserListResource, "/api/users")
    api.add_resource(DiaryResource, "/api/user/<string:user_id>/diary/<int:diary_id>")
    api.add_resource(DiaryListResource, "/api/user/<string:user_id>/diaries")
    api.add_resource(MessageListResource, "/api/diary/<string:diary_id>/messages")

    return app
