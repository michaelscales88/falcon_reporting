from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime


from app.lib.mixins import *

# TODO I need mixins for every kind of column I want at a minimum
# TODO make mixin registry


class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'sqlite'}

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


def custom_model(name, **attrs):
    mixins = (Timestamp,)
    return type(name, (Base, *mixins), {})
