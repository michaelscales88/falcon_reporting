from pandas import DataFrame
from sqlalchemy import Column
from app import db
# from app.models.custom_model import model_factory
from app.src.mixins import COLUMNS


class QueryDecoder(object):
    # TODO this is the place to check for a model in a model registry

    def decode_result(self, name, records):
        data = self.coerce_result_(records)
        name, columns, table_info = self.make_meta_data_(name, data)
        return name, columns, table_info

    @staticmethod
    def coerce_result_(result):
        return DataFrame(
            # [zip(row.keys(), row) for row in result if hasattr(row, 'keys')]  # Bind the column name to each value
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
            '__searchable__': [name for name, column in columns.items() if isinstance(column.type, db.Text)]
        }
        return table_info['__tablename__'], columns, table_info

    @staticmethod
    def model_info(model):
        print(model)
        print(model.__name__)
        print(model.__base__)
        print(model.__tablename__)
        print(model.__searchable__)
        print(model.__table_args__)
        print(model.__table__.columns.keys())
