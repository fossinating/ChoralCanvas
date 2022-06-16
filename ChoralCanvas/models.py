import datetime
import enum
import math
import uuid

from sqlalchemy.dialects.postgresql import UUID

from database import Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy import create_engine, Enum
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
    String, ForeignKey, Text, SmallInteger


class CanvasAccess(enum.Enum):
    PUBLIC = 1
    GROUP = 2
    LOC = 3


class Canvas(Base):
    __tablename__ = 'canvas'
    id = Column(String(12), primary_key=True)
    owner = Column('owner_id', UUID(as_uuid=True), ForeignKey('user.id'))
    max_paint = Column(Integer)
    width = Column(SmallInteger)
    height = Column(SmallInteger)
    # paint recharge times are saved in minutes, granting recharge_amount every recharge_time minutes
    paint_recharge_amount = Column(Integer)
    paint_recharge_time = Column(Integer)
    allow_anonymous = Column(Boolean)
    access = Column(Enum(CanvasAccess))

    def can_user_access(self, user):
        if self.access == CanvasAccess.PUBLIC:
            return True
        elif self.access == CanvasAccess.GROUP:
            return False  # test if user is in group
        elif self.access == CanvasAccess.LOC:
            raise NotImplementedError("Location based access not implemented yet")  # not implemented yet


class Mark(Base):
    __tablename__ = "canvas_mark"
    id = Column(Integer, primary_key=True)
    canvas_id = Column(String(12), ForeignKey('canvas.id'))
    canvas = relationship('Canvas',
                          backref=backref('marks', lazy='dynamic'))
    startX = Column(SmallInteger)
    startY = Column(SmallInteger)
    endX = Column(SmallInteger)
    endY = Column(SmallInteger)
    color = Column(String(8))
    lineWidth = Column(SmallInteger)
    lineCap = Column(String(8))
    marker_id = Column(UUID(as_uuid=True), ForeignKey('user.id'))
    marker = relationship('User',
                          backref=backref('marks', lazy='dynamic'))

    def to_dict(self):
        return {
            "startPos": {
                "x": self.startX,
                "y": self.startY
            },
            "endPos": {
                "x": self.endX,
                "y": self.endY
            },
            "color": self.color,
            "lineWidth": self.lineWidth,
            "lineCap": self.lineCap
        }


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

    def get_paint_level(self, canvas):
        return UserPaintLevel.query.filter_by(user=self, canvas=canvas).first()


class UserPaintLevel(Base):
    __tablename__ = "user_paint_level"
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True)
    user = relationship("User", backref=backref("paint_levels", lazy="dynamic"))
    canvas_id = Column(String(12), ForeignKey('canvas.id'), primary_key=True)
    canvas = relationship("Canvas")
    level = Column(Integer)
    last_updated_at = Column(DateTime)

    def get_paint_level(self):
        # calculate the updated paint level taking into account the time changes
        # paint recharge times are saved in minutes, granting recharge_amount every recharge_time minutes
        current_time = datetime.datetime.utcnow()
        current_minute_interval = math.floor(current_time.timestamp() / 60 / self.canvas.paint_recharge_time)
        last_updated_minute_interval = math.floor(self.last_updated_at.timestamp()
                                                  / 60 / self.canvas.paint_recharge_time)
        self.level = min(self.canvas.max_paint,
                         self.level + self.canvas.paint_recharge_amount *
                         (current_minute_interval - last_updated_minute_interval))
        # update last_updated_at
        self.last_updated_at = current_time

        # return level
        return self.level

    def reduce_paint_level(self, amount):
        # return true or false based on if user has enough paint to reduce, using get_paint_level
        if self.get_paint_level() >= amount:
            self.level -= amount
            return True
        else:
            return False
        # https://stackoverflow.com/questions/13304471/javascript-get-code-to-run-every-minute for client side
