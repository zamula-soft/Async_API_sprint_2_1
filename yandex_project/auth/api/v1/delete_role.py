from http import HTTPStatus
from flask import request
from models import Role
from db import db

logger = get_logger('api_role_delete')


@auth_blueprint.route('/delete-role', methods=('POST',))
def delete_role() -> tuple[dict, HTTPStatus]:
    """
    Insert new role
    params:
    role_name: title for the role
    """
    logger.info('Check user Admin permissions')
    current_user_id: str = session['user_id']
    if not UserRoles.user_has_role(current_user_id, 'Admin'):
        return return_response_answer(answer='The current user does not have permission to delete the role',
                                      status='error', status_code=HTTPStatus.BAD_REQUEST)

    logger.info('Deleting role')
    role_name: str = request.values.get('role')
    logger.debug(f'Get the role by name {role}')

    if Role.exist_by_name(role_name=role_name):
        role_data = Role(name=role_name)
        db.session.delete(role_data)
        db.session.commit()
        return return_response_answer(answer='The role deleted', status='ok', status_code=HTTPStatus.OK)
    return return_response_answer(answer='The role does not exist', status='ok', status_code=HTTPStatus.ACCEPTED)
