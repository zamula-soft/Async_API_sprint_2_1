from http import HTTPStatus

from flask import request
from flask_jwt_extended import verify_jwt_in_request
from werkzeug.security import check_password_hash

from models import User
from .utils import return_response_answer, auth_blueprint, return_tokens


@auth_blueprint.route('/login', methods=('POST',))
def login() -> tuple[dict, HTTPStatus]:
    """Login in account"""
    current_token = verify_jwt_in_request(optional=True)

    # Если в заголовке уже есть токен, то вход не нужен
    if current_token:
        return return_response_answer(answer='Already logged in', status='ok', status_code=HTTPStatus.ACCEPTED)

    email = request.values.get('email')
    password = request.values.get('password')

    user = User.query.filter_by(email=email).first()
    if not user:
        return return_response_answer(answer='User is not found', status='error', status_code=HTTPStatus.NOT_FOUND)

    if user.is_confirm is False:
        return return_response_answer(answer='User is not activated', status_code=HTTPStatus.NOT_FOUND, status='error')

    if check_password_hash(user.password, password):
        return return_tokens(user=user)

    return return_response_answer(answer='Password is wrong', status_code=HTTPStatus.BAD_REQUEST, status='error')
