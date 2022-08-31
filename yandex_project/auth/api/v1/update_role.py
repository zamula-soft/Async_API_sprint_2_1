from http import HTTPStatus
from flask import request
from models import Role
from db import db

logger = get_logger('api_role_update')


@auth_blueprint.route('/update-role', methods=('POST',))
def update_role() -> tuple[dict, HTTPStatus]:
    """
    Update the role
    params:
    role_name: title for the role
    new_role_name: new title for the role
    """
    logger.info('Check user Admin permissions')
    current_user_id = session['user_id']
    if not UserRoles.user_has_role(current_user_id, 'Admin'):
        return return_response_answer(answer='The current user does not have permission to add the role',
                                      status='error', status_code=HTTPStatus.BAD_REQUEST)

    logger.info('Updating role')
    role_name: str = request.values.get('role_name')
    role = Role.query.filter_by(name=role_name).first()
    logger.debug(f'Get the role by name {role}')
    new_role: str = request.values.get('new_role_name')
    if Role.exist_by_name(role_name=role_name):
        db.session.query(Role).filter(role_id=role.id).update({'name': new_role})
        db.session.commit()
        return return_response_answer(answer='The role updated', status='ok', status_code=HTTPStatus.OK)
    else:
        db.session.add(new_role)
        db.session.commit()
        return return_response_answer(answer='The role is absent and added', status='ok',
                                      status_code=HTTPStatus.ACCEPTED)
