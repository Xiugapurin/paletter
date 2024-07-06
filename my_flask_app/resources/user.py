from flask import g
from flask_restful import Resource, reqparse
from my_flask_app.extensions import db
from my_flask_app.models import User

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, help="Name of the user")
parser.add_argument("llm_preference", type=str, help="LLM Preference of the user")
parser.add_argument("profile_picture", type=str, help="Profile picture URL of the user")


class UserResource(Resource):
    def get(self):
        user_id = g.user_id

        user = User.query.filter_by(user_id=user_id).first()

        if not user:
            user = User(user_id=user_id, name="", llm_preference="", profile_picture="")
            db.session.add(user)
            db.session.commit()
            print("user created: ", user_id)

        return user.to_dict()

    def put(self):
        user_id = g.user_id
        user = User.query.get_or_404(user_id)
        args = parser.parse_args()
        user.name = args.get("name", user.name)
        user.llm_preference = args.get("llm_preference", user.llm_preference)
        user.profile_picture = args.get("profile_picture", user.profile_picture)
        db.session.commit()

        return user.to_dict()


class UserListResource(Resource):
    def get(self):
        users = User.query.all()

        return [user.to_dict() for user in users]

    def post(self):
        args = parser.parse_args()
        new_user = User(
            user_id=args["user_id"],
            name=args["name"],
            llm_preference=args.get("llm_preference"),
            profile_picture=args.get("profile_picture"),
        )
        db.session.add(new_user)
        db.session.commit()

        return new_user.to_dict(), 201
