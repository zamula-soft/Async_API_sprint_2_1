from http import HTTPStatus
from flask import request
from models import User, Role, User_Role
from db import db


@auth_blueprint.route('/delete_user_role', methods=('POST',))
def delete_user_role() -> tuple[dict, HTTPStatus]:
    """
    Delete the role for the user
    params:
    user_id: id for a user
    """
    logger = get_logger('api_user_role_add')
    logger.info('Creating role')
    email = request.values.get('email')
    logger.debug(f'Get the email - {email}')
    user = User.query.filter_by(email=email).first()
    logger.debug(f'Get the user {user}')

    role_name = request.values.get('add_role')
    role = Role.query.filter_by(name=role_name).first()
    logger.debug(f'Get the role {role}')

    user_has_role = UserRole.get_row_by_ids(user_id=user_id, role_id=role_id)

    if user_has_role is not None:
        user_role_data = User_Role(user.id, role.id)
        db.session.delete(user_role_data)
        db.session.commit()
        return return_response_answer(answer='The role deleted', status='ok', status_code=HTTPStatus.OK)
    return return_response_answer(answer='Does not have the role', status='error', status_code=HTTPStatus.NOT_FOUND)
