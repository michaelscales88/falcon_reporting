from pandas import DataFrame
from sqlalchemy import Column, Text, DateTime
import numpy as np
from datetime import datetime

# from app import db


COLUMNS = {
    np.object_: Text,
    np.int64: Text,
    np.datetime64: DateTime,
    datetime: DateTime
}


class QueryDecoder(object):
    # TODO this is the place to check for a model in a model registry

    def decode_result(self, name, records):
        data = self.coerce_result_(records)
        name, columns, table_info = self.make_meta_data_(name, data)
        return name, columns, table_info

    @staticmethod
    def coerce_result_(result):
        return DataFrame(
            result
        )

    @staticmethod
    def coerce_model_(result):
        return DataFrame.from_records(
            [q.to_dict() for q in result if hasattr(q, 'to_dict')]      # Convert a custom model back into a DataFrame
        )

    @staticmethod
    def make_meta_data_(table_name, data):
        col_types = zip(list(data), data.dtypes)
        columns = {
            name: Column(name, COLUMNS.get(d.type, None))   # Column name: Column(name, Type)
            for name, d in col_types
        }
        table_info = {
            '__tablename__': table_name,
            '__table_args__': {
                'autoload': False,
                # 'schema': 'data',
                # 'autoload_with': db.engine,

            },
            '__searchable__': [name for name, column in columns.items() if isinstance(column.type, Text)]
        }
        return table_info['__tablename__'], columns, table_info

    @staticmethod
    def make_searchable(model):
        search_attributes = [name for name, column in {}.items() if isinstance(column.type, Text)]
        return setattr(model, '__searchable__', search_attributes)

    @staticmethod
    def model_info(model):
        print(model)
        print('name', model.__name__)
        print('base', model.__base__)
        print('tablename', model.__tablename__)
        print('searchable', model.__searchable__)
        print(model.__table_args__)
        print(model.__table__.columns.keys())
