from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext import mutable
from sqlalchemy.ext.declarative import declarative_base

from app.lib.json_encoders import *

Base = declarative_base()


class FlexibleStorage(Base):
    __tablename__ = 'flexible_storage'
    # __table_args__ = {
    #     'mysql_engine': 'InnoDB'
    # }
    # __mapper_args__ = {
    #     'concrete': True
    # }

    id = Column('id', Integer, primary_key=True)
    data = Column('json_data', JsonEncodedDict)
    created_on = Column('created_on', DateTime(), default=datetime.now)
    updated_on = Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    start = Column('start_time', DateTime(timezone=True))
    end = Column('end_time', DateTime(timezone=True))

    unique_id1 = Column('receiving_party', Integer)
    unique_id2 = Column('calling_party', Integer)

    @staticmethod
    def mutable():
        mutable.MutableDict.associate_with(JsonEncodedDict)  # Toggle this to make the JSON data mutable

    @property
    def columns(self):
        """Return the value in the column, or the data type if no value is set"""
        return [
            (p.key, getattr(self, p.key) if getattr(self, p.key) else p.columns[0].type)
            for p in [
                self.__mapper__.get_property_by_column(c) for c in self.__mapper__.columns
            ]
        ]

    # TODO explore whether this can handle json.dumps directly -> remove dumps from data_center
    def __repr__(self):
        """Default representation of table"""
        return "{table_name} pk={pk} ({columns})".format(
            table_name=self.__tablename__ if self.__tablename__ else self.__class__.__name__,
            pk=getattr(self, 'id'),
            columns=', '.join(['{0}={1!r}'.format(*_) for _ in self.columns if _ != 'id'])
        )
