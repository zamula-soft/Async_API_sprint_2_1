from datetime import datetime
from random import randint, sample, shuffle
from re import match
from http import HTTPStatus

from flask import Blueprint, make_response
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash
from werkzeug.local import LocalProxy

from db import db
from models import AuthHistory, User


auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


def check_valid_email(user_email: str) -> bool:
    """
    Function for check valid email
    :param user_email:
    :return:
    """
    tpl_email = '^(?=.{1,64}@)[A-Za-z0-9_-]+(\\.[A-Za-z0-9_-]+)*@[^-][A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*(\\.[A-Za-z]{2,})$'
    if match(tpl_email, user_email):
        return True
    return False


def generate_password() -> generate_password_hash:
    """Generate hash password"""
    symbols = '+-/*!&$#?=@<>_'
    numbers = '1234567890'
    letters = 'abcdefghijklnopqrstuvwxyz'

    password = sample(symbols, randint(1, 2)) + sample(numbers, randint(1, 2)) + sample(letters.upper(), randint(1, 2))
    password += sample(letters, 8 - len(password))
    shuffle(password)

    return generate_password_hash(''.join(password))


def check_valid_password(password: str) -> bool:
    """
    Check password.
    :param password:
    :return:
    """
    symbols = '+-/*!&$#?=@<>_'
    numbers = '1234567890'
    letters = 'abcdefghijklnopqrstuvwxyz'

    criteria = [
        len(set(symbols) & set(password)) > 0,
        len(set(numbers) & set(password)) > 0,
        len(set(letters) & set(password)) > 0,
        len(set(letters.upper()) & set(password)) > 0,
        len(password) >= 8
    ]

    if all(criteria):
        return True

    return False


def send_email():
    """Function for send email."""
    pass


def return_error_answer(answer: str) -> make_response:
    """
    Function for send error.
    :param answer:
    :return:
    """
    return make_response(
        {
            "message": answer,
            "status": "error"
        }, HTTPStatus.BAD_REQUEST)


def return_tokens(user: User) -> tuple:
    """
    Function for send tokens.
    :param user:
    :return:
    """
    claims = {
        'name': user.name,
    }

    access_token = create_access_token(identity=user.email,
                                       additional_claims=claims)
    refresh_token = create_refresh_token(identity=user.email,
                                         additional_claims=claims)
    return ({'access_token': access_token, 'refresh_token': refresh_token},
            HTTPStatus.OK)


def add_auth_history(user: User, request: LocalProxy) -> None:
    """Function for save history in db"""
    agent = request.user_agent

    auth = AuthHistory(user_id=user.id, browser=agent.browser,
                       platform=agent.platform, timestamp=datetime.now())

    db.session.add(auth)
    db.session.commit()
