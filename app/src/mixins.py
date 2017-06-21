from sqlalchemy import Integer, String, Column
from sqlalchemy.types import DateTime
import numpy as np
from numpy import object_, int64
from sqlalchemy_utils import Timestamp, generic_repr       # sqlalchemy provided mixins
from datetime import datetime


COLUMNS = {
    np.object_: String,
    int64: Integer,
    np.datetime64: DateTime,
    datetime: DateTime
}


@generic_repr                                           # nice prebuilt __repr__ for all models
class BaseMixin(Timestamp):                             # include created_on and updated_on columns for all models
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

    def __repr__(self):
        """Default representation of table"""
        return "{table_name} pk={pk} ({columns})".format(
            table_name=self.__tablename__ if self.__tablename__ else self.__class__.__name__,
            pk=getattr(self, 'id'),
            columns=', '.join(['{0}={1!r}'.format(*_) for _ in self.columns if _ != 'id'])
        )
