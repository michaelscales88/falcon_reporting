from sqlalchemy.orm import defer
from datetime import datetime
from json import dumps
from pandas import DataFrame, read_sql
from sqlalchemy import Column, String, Integer
import numpy as np


from app.fixtures.base_test import BaseTest
from app.src.factory import model_factory
from app.lib.mixins import COLUMNS
from app.lib.query_decoder import QueryDecoder


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
        # clients = ['Susy', 'Josh', 'Sally', 'Emily']
        # all_call_data = self.example_data_src.example(datetime.today().date(), clients)
        # print(all_call_data)
        # data = DataFrame(
        #     all_call_data
        # )
        decoder_ring = QueryDecoder()
        with TestCustomModel.app.app_context():
            src, result = self.query_statement(
                TestCustomModel.app.config['TEST_STATEMENT'],
                TestCustomModel.app.config['EXTERNAL_CONNECTION']
            )
            # data_src_records = [dict(zip(row.keys(), row)) for row in result]   # Bind the column name to each value
            # data = DataFrame(
            #     data_src_records
            # )
        model, data = decoder_ring.decode_result(result)
        # data.set_index('call_id', inplace=True)                             # Make the call_id the row index
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
        with TestCustomModel.app.app_context():
            conn = self.internal_connection(
                TestCustomModel.app.config['SQLALCHEMY_DATABASE_URI'],
                # echo=TestCustomModel.app.config['SQLALCHEMY_ECHO'],
                echo=False,
                cls=model
            )
        for index, row in data.iterrows():
            # a_model = model(id=index, **row)        # this doesn't work because there are more than one call_id
            a_model = model(**row)                  # this works but the index is incremented
            # print(a_model)
            conn.add(a_model)
        conn.commit()
        query = conn.query(model).all()
        df = DataFrame.from_records([q.to_dict() for q in query])
        df.set_index(['call_id', 'event_id'], inplace=True)     # This groups by call_id and then event_id
        # df = DataFrame(query.all(), columns=[column['name'] for column in query.column_descriptions])
        print(df)
        self.assertTrue(True)
