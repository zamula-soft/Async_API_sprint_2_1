from flask_jwt_extended import get_jwt_identity
from models  import User, Role, User_Role
from db import db


class ReadUserRole:
    def read_user_roles(self, role):
        """
        Get the role for the user
        params:
        user_id: id for a user
        """
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        return UserRole.get_row_by_ids(user_id=user_id, role_id=role_id)
