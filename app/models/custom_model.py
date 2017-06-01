from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from datetime import datetime


from app.lib.mixins import *


@generic_repr                                           # nice prebuilt __repr__ for all models
class BaseMixin(object):
    id = Column(Integer, primary_key=True)


def apply_mixins(cls, column_data):
    for name, value in column_data.items():             # bind as class attributes before inst
        setattr(cls, name, value)
    return cls


class MixedModel(object):
    pass


Base = declarative_base(cls=BaseMixin)


def get_model(name, columns, table_info):
    my_mixin = apply_mixins(MixedModel, columns)        # get a mixed model with specified model
    return type(name, (Base, my_mixin), table_info)     # return Model object
