from app import db
# from sqlalchemy.types import Integer, Text, DateTime
from sqlalchemy_utils import Timestamp, generic_repr       # sqlalchemy provided mixins
from sqlalchemy.ext.declarative import declarative_base


@generic_repr                                           # nice prebuilt __repr__ for all models
class _Base(object):                             # include created_on and updated_on columns for all models
    __tablename__ = 'base'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.Text)
    query = db.session.query_property()

    @property
    def columns(self):
        """Return the value in the column, or the data type if no value is set"""
        return [
            (p.key, getattr(self, p.key) if getattr(self, p.key) else p.columns[0].type)
            for p in [
                self.__mapper__.get_property_by_column(c) for c in self.__mapper__.columns
                ]
        ]

    # def to_dict(self):
    #     return {
    #         k: v for k, v in self.columns               # lets us easily convert back to DataFrame
    #     }


Base = declarative_base(cls=(_Base, Timestamp))

