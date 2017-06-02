from pandas import DataFrame
from sqlalchemy import Column

from app.lib.mixins import COLUMNS
from app.models.custom_model import get_model


class QueryDecoder(object):
    # TODO this is the place to check for a model in a model registry

    def decode_result(self, result):
        data = self.coerce_result_(result)
        name, columns, table_info = self.make_meta_data_(data)
        model = get_model(name, columns, table_info)
        self.model_info(model)
        return model, data

    @staticmethod
    def coerce_result_(result):
        return DataFrame(
            [dict(zip(row.keys(), row)) for row in result if hasattr(row, 'keys')]  # Bind the column name to each value
        )

    @staticmethod
    def coerce_model_(result):
        return DataFrame.from_records(
            [q.to_dict() for q in result if hasattr(q, 'to_dict')]      # Convert a custom model back into a DataFrame
        )

    @staticmethod
    def make_meta_data_(data):
        columns = {
            # col_name: Column(col_name, col_type, table=None)
            name: Column(name, COLUMNS.get(d.type, None)) for name, d in zip(list(data), data.dtypes)
        }
        table_info = {
            '__tablename__': 'sla_report',
            '__table_args__': {
                'autoload': False
            }
        }
        return table_info['__tablename__'], columns, table_info

    @staticmethod
    def model_info(model):
        print(model)
        print(model.__name__)
        print(model.__base__)
        print(model.__tablename__)
        print(model.__table_args__)
        print(model.__table__.columns.keys())
