from sqlalchemy.orm import defer
from datetime import datetime
from json import dumps
from pandas import DataFrame
from sqlalchemy import Column, String, Integer
import numpy as np


from app.fixtures.base_test import BaseTest
from app.src.factory import model_factory
from app.lib.mixins import COLUMNS


class TestCustomModel(BaseTest):
    def setUp(self):
        super().setUp()

    def test_columns(self):
        table_info = {
            '__tablename__': 'test_report',
            '__table_args__': {
                'autoload': False
            }
        }
        columns = {
            'string': Column('string', String(20)),
            'integer': Column('integer', Integer()),

        }
        model = model_factory(columns, table_info)
        print(model)
        print(model.__base__)
        print(model.__tablename__)
        print(model.__table_args__)
        print(model.__table__.columns.keys())
        del model
        self.assertTrue(True)

    def test_identify_columns(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        all_call_data = self.example_data_src.example(datetime.today().date(), clients)
        print(all_call_data)
        data = DataFrame(
            all_call_data
        )
        # data.set_index('call_id', inplace=True)
        # print(data.dtypes)
        # print(data)
        # for call_id, call_data in all_call_data:
        #     print(call_id)
        #
        #     inner_data = DataFrame(
        #         call_data
        #     )
        #     print(inner_data)
        #     print(inner_data.dtypes)
        #     print(call_data.keys())
        #     break
        # with TestCustomModel.app.app_context():
        #     src, result = self.query_statement(
        #         TestCustomModel.app.config['TEST_STATEMENT'],
        #         TestCustomModel.app.config['EXTERNAL_CONNECTION']
        #     )
        #     data_src_records = [dict(zip(row.keys(), row)) for row in result]   # Bind the column name to each value
        #     data = DataFrame(
        #         data_src_records
        #     )
        # data.set_index('call_id', inplace=True)                             # Make the call_id the row index
        # build column metadata
        # print([item for item in data.items()])
        # print(data.dtypes)
        # columns = {
        #     # col_name: Column(col_name, col_type, table=None)
        #     name: Column(name, COLUMNS.get(d.type, None)) for name, d in zip(list(data), data.dtypes)
        # }
        # table_info = {
        #     '__tablename__': 'sla_report',
        #     '__table_args__': {
        #         'autoload': False
        #     }
        # }
        # model = model_factory(columns, table_info, name='Test')
        # print(model)
        # print(model.__base__)
        # print(model.__tablename__)
        # print(model.__table_args__)
        # print(model.__table__.columns.keys())
        # with TestCustomModel.app.app_context():
        #     conn = self.internal_connection(
        #         TestCustomModel.app.config['SQLALCHEMY_DATABASE_URI'],
        #         echo=TestCustomModel.app.config['SQLALCHEMY_ECHO'],
        #         cls=model
        #     )
        # for index, row in data.iterrows():
        #     # a_model = model(id=index, **row)        # this doesn't work because there are more than one call_id
        #     a_model = model(**row)                  # this works but the index is incremented
        #     print(a_model)
        #     conn.add(a_model)
        # conn.commit()
        # foo = conn.query(model).options().all()  # this lets you specify repr order
        # print(foo)
        self.assertTrue(True)
