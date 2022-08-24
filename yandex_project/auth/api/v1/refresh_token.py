from http import HTTPStatus

from flask_jwt_extended import get_jwt_identity, jwt_required

from models import User

from .utils import auth_blueprint, return_tokens


@jwt_required(refresh=True)
@auth_blueprint.route('/refresh-token', methods=('POST',))
def refresh_token() -> tuple[dict, HTTPStatus]:
    """
    Register on site.
    :return:
    """
    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    return return_tokens(user=user)
