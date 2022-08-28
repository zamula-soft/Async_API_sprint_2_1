from flask_jwt_extended import get_jwt_identity
from models import User, Role, User_Role
from db import db


class CreateUserRole:
    def create_user_role(self, role):
        """
        Insert the role for the user
        params:
        user_id: id for a user
        """
        current_user = get_jwt_identity()
        user = User.query.filter_by(email=current_user).first()

        user_has_role = User_Role.query.filter(user_id=user.id, role_id=role.id).first()
        if user_has_role is None:
            user_role_data = User_Role(user.id, role.id)
            db.session.add(user_role_data)
            db.session.commit()
