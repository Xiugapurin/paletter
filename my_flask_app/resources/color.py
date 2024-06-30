from datetime import datetime
from flask import g
from flask_restful import Resource, reqparse
from my_flask_app import db
from my_flask_app.models import Color

parser = reqparse.RequestParser()
parser.add_argument("content", type=str)


class ColorListResource(Resource):
    def get(self):
        pass

    def post(self):
        pass
