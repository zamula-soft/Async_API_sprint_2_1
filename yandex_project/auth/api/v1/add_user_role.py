from http import HTTPStatus
from flask import request
from models import User, Role, UserRoles
from db import db

logger = get_logger('api_user_role_add')


@auth_blueprint.route('/add-role-to-user', methods=('POST',))
def add_role_to_user() -> tuple[dict, HTTPStatus]:
    """
    Insert the role for the user
    params:
    user_id: id for a user
    role_name: title for the role
    """
    logger.info('Check user Admin permissions')
    current_user_id = session['user_id']
    if not UserRoles.user_has_role(current_user_id, 'Admin'):
        return return_response_answer(answer='The current user does not have permission to add the role',
                                      status='error', status_code=HTTPStatus.BAD_REQUEST)

    logger.info('Deleting role')
    user_id: str = request.values.get('user_id')
    logger.debug(f'Get the user_id {user_id}')
    role_name: str = request.values.get('role_name')
    role = Role.query.filter_by(name=role_name).first()
    logger.debug(f'Get the role {role}')

    if not UserRoles.user_has_role(user_id, role_name):
        user_role_data = UserRoles(user_id=user_id, role_id=role.id)
        db.session.add(user_role_data)
        db.session.commit()
        return return_response_answer(answer='The role added to the user', status='ok', status_code=HTTPStatus.OK)
    return return_response_answer(answer='The user already has the role', status='ok', status_code=HTTPStatus.ACCEPTED)
