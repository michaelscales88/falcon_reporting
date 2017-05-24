from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime


# TODO I need mixins for every kind of column I want at a minimum
# TODO make mixin registry
class TimeStamp(object):

    created_on = Column('created_on', DateTime(), default=datetime.now)
    updated_on = Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)


class Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __table_args__ = {'mysql_engine': 'sqlite'}

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


def custom_model(name, **attrs):
    mixins = (TimeStamp,)
    return type(name, (Base, *mixins), {})
