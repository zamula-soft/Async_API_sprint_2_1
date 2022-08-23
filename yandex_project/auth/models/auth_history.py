from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from db import db


class AuthHistory(db.Model):
    __tablename__ = 'auth_history'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)
    user_id = db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime)
    browser = db.Column(db.Text, nullable=True)
    platform = db.Column(db.Text, nullable=True)
    user_device_type = db.Column(db.Text, primary_key=True)

    def __repr__(self):
        return f'{self.timestamp}::{self.browser}::{self.platform}'
