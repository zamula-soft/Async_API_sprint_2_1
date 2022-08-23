from http import HTTPStatus
from random import randint

from flask import make_response, request

from models import User
from db import db
from auth_logger import get_logger
from .utils import send_email, check_valid_email, generate_password, auth_blueprint, return_error_answer


@auth_blueprint.route('/register', methods=('POST',))
def register() -> make_response:
    """
    Register on site.
    :return:
    """
    logger = get_logger('api_register')
    logger.info('Start work register')
    email = request.values.get('email')
    logger.debug(f'Get email - {email}')

    if not email:
        return return_error_answer('Email is empty')

    email_is_valid = check_valid_email(email)
    if email_is_valid is False:
        return return_error_answer('Email is not valid')

    user = User.query.filter_by(email=email).first()
    logger.debug(f'Check have we this user {user}')

    if user:
        logger.debug(f'We have user with this email, send error')
        return return_error_answer('Email is register')

    password = generate_password()
    name = 'user_' + str(randint(10000, 10000000))

    user = User(email=email, password=password, name=name)
    db.session.add(user)
    db.session.commit()
    send_email()
    return make_response(
            {
                "message": "New account was registered successfully",
                "status": "success"
            }, HTTPStatus.OK)

