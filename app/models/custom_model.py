from sqlalchemy_utils import generic_repr               # sqlalchemy provided mixins
from sqlalchemy import Column, Integer

from app.lib.mixins import TimeStamp
from sqlalchemy.ext.declarative import declarative_base


@generic_repr                                           # nice prebuilt __repr__ for all models
class BaseMixin(TimeStamp):                             # include created_on and updated_on columns for all models
    id = Column(Integer, primary_key=True)

    @property
    def columns(self):
        """Return the value in the column, or the data type if no value is set"""
        return [
            (p.key, getattr(self, p.key) if getattr(self, p.key) else p.columns[0].type)
            for p in [
                self.__mapper__.get_property_by_column(c) for c in self.__mapper__.columns
                ]
        ]

    def to_dict(self):
        return {
            k: v for k, v in self.columns               # lets us easily convert back to DataFrame
        }


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
