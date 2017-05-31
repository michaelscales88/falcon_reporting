from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime


from app.lib.mixins import *

# TODO make mixin registry


@generic_repr       # This adds a default to columns without data for __repr__
class BaseMixin(object):

    id = Column(Integer, primary_key=True)


# All custom models that inherit from Base get an id, created_on, updated_on
Base = declarative_base(cls=(BaseMixin, Timestamp))


def custom_model(name, attrib):
    mixins = ()
    return type(name, (Base, *mixins), attrib)
