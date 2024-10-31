from flask import g
from flask_restful import Resource, reqparse
from src.models import Paletter

parser = reqparse.RequestParser()


class PaletterListResource(Resource):
    def get(self):
        user_id = g.user_id

        paletters = Paletter.query.filter_by(user_id=user_id).all()

        return {
            "paletters": [p.to_dict() for p in paletters],
        }, 200
