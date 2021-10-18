import datetime

from flask_appbuilder._compat import as_unicode
from flask_appbuilder.security.sqla.models import assoc_user_role, User
from flask_appbuilder import Model
from flask import g
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref, relationship


class MyUser(User):
    __tablename__ = "ab_user"
    display_name = Column(String(64), nullable=False)
    #delattr(CustomUser, "first_name")
    #delattr(CustomUser, "last_name")


class CustomUser(Model):
    # i have no clue if any of this is going to work at all lmaooo
    __tablename__ = "ab_custom_user"
    id = Column(Integer, Sequence("ab_user_id_seq"), primary_key=True)
    display_name = Column(String(64), nullable=False)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(256))
    active = Column(Boolean)
    email = Column(String(64), unique=True, nullable=False)
    last_login = Column(DateTime)
    login_count = Column(Integer)
    fail_login_count = Column(Integer)
    roles = relationship("Role", secondary=assoc_user_role, backref="custom_user")
    created_on = Column(DateTime, default=datetime.datetime.now, nullable=True)
    changed_on = Column(DateTime, default=datetime.datetime.now, nullable=True)

    @declared_attr
    def created_by_fk(self):
        return Column(
            Integer, ForeignKey("ab_custom_user.id"), default=self.get_user_id, nullable=True
        )

    @declared_attr
    def changed_by_fk(self):
        return Column(
            Integer, ForeignKey("ab_custom_user.id"), default=self.get_user_id, nullable=True
        )

    created_by = relationship(
        "CustomUser",
        backref=backref("created", uselist=True),
        remote_side=[id],
        primaryjoin="CustomUser.created_by_fk == CustomUser.id",
        uselist=False,
    )
    changed_by = relationship(
        "CustomUser",
        backref=backref("changed", uselist=True),
        remote_side=[id],
        primaryjoin="CustomUser.changed_by_fk == CustomUser.id",
        uselist=False,
    )

    @classmethod
    def get_user_id(cls):
        try:
            return g.user.id
        except Exception:
            return None

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return as_unicode(self.id)

    def get_full_name(self):
        return u"{0}".format(self.display_name)

    def __repr__(self):
        return self.get_full_name()


class RegisterUser(Model):
    __tablename__ = "ab_register_user"
    id = Column(Integer, Sequence("ab_register_user_id_seq"), primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(256))
    email = Column(String(64), nullable=False)
    registration_date = Column(DateTime, default=datetime.datetime.now, nullable=True)
    registration_hash = Column(String(256))
