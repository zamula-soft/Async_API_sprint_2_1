from http import HTTPStatus
from flask import request
from models import Role
from db import db

logger = get_logger('api_role_add')


@auth_blueprint.route('/add-role', methods=('POST',))
def add_role() -> tuple[dict, HTTPStatus]:
    """
    Add new role
    params:
    role_name: title for the role
    """
    logger.info('Check user Admin permissions')
    current_user_id = session['user_id']
    if not UserRoles.user_has_role(current_user_id, 'Admin'):
        return return_response_answer(answer='The current user does not have permission to add the role',
                                      status='error', status_code=HTTPStatus.BAD_REQUEST)

    logger.info('Adding new role')
    role_name: str = request.values.get('role_name')
    role = Role.query.filter_by(name=role_name).first()
    logger.debug(f'Get the role by name {role}')
    if not Role.exist_by_name(role_name=role_name):
        new_role = Role(name=role_name)
        db.session.add(new_role)
        db.session.commit()
        return return_response_answer(answer='The role added', status='ok', status_code=HTTPStatus.OK)

    return return_response_answer(answer='Already has the role', status='ok', status_code=HTTPStatus.ACCEPTED)
