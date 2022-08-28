from http import HTTPStatus
from flask import request
from models import Role
from db import db


@auth_blueprint.route('/add_role', methods=('POST',))
def add_role() -> tuple[dict, HTTPStatus]:
    """
    Insert new role
    """
    logger = get_logger('api_role_add')
    logger.info('Creating role')

    role_name: str = request.values.get('role_name')
    logger.debug(f'Get the role by name {role}')
    if not Role.exist_by_name(role_name=role_name):
        new_role = Role(name=role_name)
        db.session.add(new_role)
        db.session.commit()
        return return_response_answer(answer='The role added', status='ok', status_code=HTTPStatus.OK)

    return return_response_answer(answer='Already has the role', status='ok', status_code=HTTPStatus.ACCEPTED)
