import enum
import uuid

from sqlalchemy.dialects.postgresql import UUID

from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
    String, ForeignKey, Text


class CanvasAccess(enum.Enum):
    PUBLIC = 1
    GROUP = 2
    LOC = 3


class Canvas(Base):
    __tablename__ = 'canvas'
    id = Column(String(12), primary_key=True)
    owner = Column('owner_id', UUID(as_uuid=True), ForeignKey('user.id'))
    max_paint = Column(Integer)
    paint_regen = Column(Integer)
    allow_anonymous = Column(Boolean)
    access = Column(Enum(CanvasAccess))
    canvas_image = Column(Text)

    def can_user_access(self, user):
        if self.access == CanvasAccess.PUBLIC:
            return True
        elif self.access == CanvasAccess.GROUP:
            return False  # test if user is in group
        elif self.access == CanvasAccess.LOC:
            raise NotImplementedError("Location based access not implemented yet")  # not implemented yet


# not even close to finalized yet
"""class CanvasLocAccess(Base):
    __tablename__ = 'canvas_loc_access'
    canvas_id = Column('canvas_id', String(255), ForeignKey('canvas.id'))
    description = Column(String(255))
"""


class CanvasGroupAccess(Base):
    __tablename__ = 'canvas_group_access'
    canvas_id = Column('canvas_id', String(12), ForeignKey('canvas.id'), primary_key=True)
    group_id = Column("group_id", UUID(as_uuid=True), ForeignKey('user.id'))


class GroupAccess(enum.Enum):
    OPEN = 1
    REQUEST = 2
    OPEN_LINKED = 3
    REQUEST_LINKED = 4
    INVITE_ONLY = 5


class Group(Base):
    __tablename__ = 'group'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(255), nullable=False)
    description = Column(String(255))
    access = Column(Enum(GroupAccess))
    members = relationship('User', secondary='groups_users',
                           backref=backref('group', lazy='dynamic'))


class LinkedAccount(Base):
    __tablename__ = "linked_accounts"
    link_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    linked_account_type = Column(String(255), nullable=False)
    link = Column(String(255), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    linked_on = Column(DateTime)


class GroupsUsers(Base):
    __tablename__ = "groups_users"
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)
    group_id = Column(UUID(as_uuid=True), ForeignKey("group.id"), primary_key=True)
    join_date = Column(DateTime())


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users',
                         backref=backref('users', lazy='dynamic'))
    groups = relationship('Group', secondary='groups_users',
                          backref=backref('users', lazy='dynamic'))
    linked_accounts = relationship("LinkedAccount")
