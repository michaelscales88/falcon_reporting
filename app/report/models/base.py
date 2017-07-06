from sqlalchemy import Column, Integer
from sqlalchemy_utils import Timestamp, generic_repr
from sqlalchemy.ext.declarative import declarative_base, declared_attr


@generic_repr
class _Base(object):

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

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
            k: v for k, v in self.columns   # lets us easily convert back to DataFrame
        }

# Timestamp includes created_on and updated_on columns for all models
# Base = declarative_base(cls=(_Base, Timestamp))

