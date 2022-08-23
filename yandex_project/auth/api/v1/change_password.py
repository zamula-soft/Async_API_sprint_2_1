from http import HTTPStatus

from flask import request
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
from db import db
from auth_logger import get_logger
from .utils import auth_blueprint, check_valid_password, return_response_answer, return_tokens


@auth_blueprint.route('/change-password', methods=('POST',))
def change_password() -> tuple[dict, HTTPStatus]:
    logger = get_logger('api_change_password')
    logger.info('Start work register')
    email = request.values.get('email')
    old_password = request.values.get('old_password')
    new_password = request.values.get('new_password')
    confirm_password = request.values.get('confirm_password')
    logger.debug(f'Get emails\nemail - {email}\n'
                 f'old_password - {old_password}\nnew_password - {new_password}\nconfirm_password - {confirm_password}')

    if not confirm_password or not old_password or not new_password:
        return return_response_answer(
            answer='Not fill all fields.', status_code=HTTPStatus.BAD_REQUEST, status='error')

    password_is_valid = check_valid_password(new_password)
    if not password_is_valid:
        return return_response_answer(
            answer='Password is not valid', status_code=HTTPStatus.BAD_REQUEST, status='error')

    if new_password != confirm_password:
        return return_response_answer(
            answer='Passwords are different', status_code=HTTPStatus.BAD_REQUEST, status='error')

    user = User.query.filter_by(email=email).first()
    logger.debug(f'Check have we this user {user}')

    if not user:
        logger.debug(f'We have not user with this email, send error')
        return return_response_answer(
            answer='We have not this user', status_code=HTTPStatus.BAD_REQUEST, status='error')

    right_password = check_password_hash(user.password, old_password)
    if right_password is False:
        logger.debug(f'Password is wrong for this user')
        return return_response_answer(answer='Wrong password', status_code=HTTPStatus.BAD_REQUEST, status='error')

    if user.is_confirm is False:
        logger.debug(f'It is first change password')
        user.is_confirm = True

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return return_tokens(user=user)
