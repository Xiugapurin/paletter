from flask import Flask
from config import Config
from .extensions import db, migrate
from flask_restful import Api
from my_flask_app.resources.user import UserResource, UserListResource
from my_flask_app.resources.diary import DiaryResource, DiaryListResource


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    api = Api(app)
    api.add_resource(UserResource, "/api/user/<string:user_id>")
    api.add_resource(UserListResource, "/api/users")
    api.add_resource(
        DiaryResource, "/api/users/<string:user_id>/diaries/<int:diary_id>"
    )
    api.add_resource(DiaryListResource, "/api/users/<string:user_id>/diaries")

    return app
