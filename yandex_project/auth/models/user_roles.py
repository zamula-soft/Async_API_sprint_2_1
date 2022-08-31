import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import db
from models import Role, User


class UserRoles(db.Model):
    __tablename__ = 'user_role'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('roles.id', ondelete='CASCADE'))

    user = db.relationship(User, backref=db.backref("user_role", lazy=True))
    role = db.relationship(Role, backref=db.backref("user_role", lazy=True))

    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="user_role_pk"),)

    def __repr__(self) -> str:
        return f'<UserRole {self.user_id}:{self.role_id}>'

    @classmethod
    def user_has_role(cls, user_id: str, role_id: str) -> bool:
        return cls.query.filter(cls.user_id == user_id, cls.role_id == role_id).first()
