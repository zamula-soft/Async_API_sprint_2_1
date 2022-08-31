from http import HTTPStatus
from flask import request
from models import Role
from db import db

logger = get_logger('api_role_add')


@auth_blueprint.route('/read-all-roles', methods=('GET',))
def read_all_roles() -> tuple[dict, HTTPStatus]:
    """
    Read all roles
    """
    logger.info('Check user Admin permissions')
    current_user_id = session['user_id']
    if not UserRoles.user_has_role(current_user_id, 'Admin'):
        return return_response_answer(answer='The current user does not have permission to add the role',
                                      status='error', status_code=HTTPStatus.BAD_REQUEST)

    logger.info('Read all roles')
    roles = Role.query_all()
    return return_response_answer(answer=roles, status='ok', status_code=HTTPStatus.OK)
