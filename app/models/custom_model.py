from sqlalchemy.ext.declarative import declarative_base

from app.src.mixins import BaseMixin


def apply_mixins(cls, column_data):
    for name, value in column_data.items():             # bind as class attributes before inst
        setattr(cls, name, value)
    return cls


class MixedModel(object):
    pass


Base = declarative_base(cls=BaseMixin)


def model_factory(name, columns, table_info):
    my_mixin = apply_mixins(MixedModel, columns)        # get a mixed model with correct column types
    return type(name, (Base, my_mixin), table_info)     # return Model object
