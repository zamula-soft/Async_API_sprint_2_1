from http import HTTPStatus
from flask import request
from models import User, Role, User_Role
from db import db


@auth_blueprint.route('/has_user_role', methods=('POST',))
def get_user_role() -> tuple[dict, HTTPStatus]:
    logger = get_logger('api_user_role_read')
    logger.info('Reading role')
    email = request.values.get('email')
    logger.debug(f'Get the email - {email}')
    user = User.query.filter_by(email=email).first()
    logger.debug(f'Get the user {user}')

    role_name = request.values.get('read_role')
    role = Role.query.filter_by(name=role_name).first()
    logger.debug(f'Get the role {role}')

    user_has_role = UserRole.get_row_by_ids(user_id=user_id, role_id=role_id)
    if user_has_role is None:
        return return_response_answer(answer='User does not have the role', status='error', status_code=HTTPStatus.NOT_FOUND)
    return return_response_answer(answer='User has the role', status='ok', status_code=HTTPStatus.OK)
