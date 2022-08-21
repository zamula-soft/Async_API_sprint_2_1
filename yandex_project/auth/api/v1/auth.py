from http import HTTPStatus
from random import randint
from logging import getLogger, DEBUG, StreamHandler, Formatter
import sys

from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from models import User
from db import db


auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


@auth_blueprint.route('/register', methods=('POST',))
def register():
    logger.info('Start work register')
    email = request.values.get('email')
    logger.debug(f'Get email - {email}')

    if not email:
        return make_response(
            {
                "message": "email is empty",
                "status": "error"
            }, HTTPStatus.BAD_REQUEST)

    user = User.query.filter_by(email=email).first()

    if user is not None:
        return make_response(
            {
                "message": "The username is already in use",
                "status": "error"
            }, HTTPStatus.BAD_REQUEST)

    password = 123
    name = 'user_' + str(randint(10000, 10000000))

    user = User(email=email, password=password, name=name)
    db.session.add(user)
    db.session.commit()
    return make_response(
            {
                "message": "New account was registered successfully",
                "status": "success"
            }, HTTPStatus.OK)
