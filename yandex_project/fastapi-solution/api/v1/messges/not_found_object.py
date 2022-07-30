from http import HTTPStatus

from fastapi import HTTPException


def message_not_found(name_object: str, id_object: str) -> HTTPException:
    """Return message if not found object."""
    return HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f'{name_object} with uuid {id_object} not found.')
