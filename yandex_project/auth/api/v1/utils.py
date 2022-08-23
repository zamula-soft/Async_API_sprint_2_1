from random import randint, sample, shuffle
from re import match
from http import HTTPStatus

from flask import Blueprint, make_response
from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.security import generate_password_hash


auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


def check_email(user_email: str) -> bool:
    tpl_email = '^(?=.{1,64}@)[A-Za-z0-9_-]+(\\.[A-Za-z0-9_-]+)*@[^-][A-Za-z0-9-]+(\\.[A-Za-z0-9-]+)*(\\.[A-Za-z]{2,})$'
    if match(tpl_email, user_email):
        return True
    return False


def generate_password():
    symbols = '+-/*!&$#?=@<>_'
    numbers = '1234567890'
    letters = 'abcdefghijklnopqrstuvwxyz'

    password = sample(symbols, randint(1, 2)) + sample(numbers, randint(1, 2)) + sample(letters.upper(), randint(1, 2))
    password += sample(letters, 8 - len(password))
    shuffle(password)

    return generate_password_hash(''.join(password))


def check_valid_password(password: str) -> bool:
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
    pass


def return_error_answer(answer: str) -> make_response:
    return make_response(
        {
            "message": answer,
            "status": "error"
        }, HTTPStatus.BAD_REQUEST)


def return_tokens(user):
    claims = {
        'name': user.name,
    }

    access_token = create_access_token(identity=user.email,
                                       additional_claims=claims)
    refresh_token = create_refresh_token(identity=user.email,
                                         additional_claims=claims)
    return ({'access_token': access_token, 'refresh_token': refresh_token},
            HTTPStatus.OK)
