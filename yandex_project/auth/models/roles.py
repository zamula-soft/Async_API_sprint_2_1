import uuid
from sqlalchemy.dialects.postgresql import UUID
from db import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)

    def __init__(self):
        if not self.exist_by_name('Admin'):
            admin_role = Role(name='Admin')
            db.session.add(admin_role)
            db.session.commit()

    def __repr__(self):
        return f'Role {self.name} {self.id}'

    @classmethod
    def exist_by_name(cls, role_name: str) -> bool:
        return db.session.query(
            cls.query.filter(cls.name == role_name).exists()
        ).scalar()

    @classmethod
    def query_all(cls):
        return db.session.query(
            cls.query(Role).all()
        )
