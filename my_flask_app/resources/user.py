from flask_restful import Resource, reqparse
from my_flask_app.extensions import db
from my_flask_app.models import User

parser = reqparse.RequestParser()
parser.add_argument("user_id", type=str, required=True, help="User ID is required")
parser.add_argument("name", type=str, required=True, help="Name is required")
parser.add_argument("llm_preference", type=str)
parser.add_argument("profile_picture", type=str)


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)

        return user.to_dict()

    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = parser.parse_args()
        user.name = args.get("name", user.name)
        user.llm_preference = args.get("llm_preference", user.llm_preference)
        user.profile_picture = args.get("profile_picture", user.profile_picture)
        db.session.commit()

        return user.to_dict()

    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return "", 204


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
