from http import HTTPStatus
from random import randint, sample, shuffle
from re import match

from flask import Blueprint, make_response, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
from db import db
from auth_logger import get_logger
from .utils import send_email, check_email, generate_password, auth_blueprint


@auth_blueprint.route('/register', methods=('POST',))
def register():
    logger = get_logger('api_register')
    logger.info('Start work register')
    email = request.values.get('email')
    logger.debug(f'Get email - {email}')

    if not email:
        return make_response(
            {
                "message": "email is empty",
                "status": "error"
            }, HTTPStatus.BAD_REQUEST)

    email_is_email = check_email(email)
    if not email_is_email:
        return make_response(
            {
                "message": "email is not email",
                "status": "error"
            }, HTTPStatus.BAD_REQUEST)

    user = User.query.filter_by(email=email).first()
    logger.debug(f'Check have we this user {user}')

    if user:
        logger.debug(f'We have user with this email, send error')
        return make_response(
            {
                "message": "The email is already in use",
                "status": "error"
            }, HTTPStatus.BAD_REQUEST)

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

