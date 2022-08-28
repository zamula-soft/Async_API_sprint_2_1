import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import db
from models import Role, User


class UserRole(db.Model):
    __tablename__ = 'user_role'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    role_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)

    user = db.relationship(User, backref=db.backref("user_role", lazy=True))
    role = db.relationship(Role, backref=db.backref("user_role", lazy=True))

    __table_args__ = (db.UniqueConstraint("user_id", "role_id", name="user_role_pk"),)

    def __repr__(self) -> str:
        return f'<UserRole {self.user_id}:{self.role_id}>'