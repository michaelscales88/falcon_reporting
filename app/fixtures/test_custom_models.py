from sqlalchemy.orm import defer
from datetime import datetime
from json import dumps
from pandas import DataFrame
from sqlalchemy import Column, String, Integer


from app.fixtures.base_test import BaseTest
from app.src.factory import model_factory
from app.lib.json_encoders import MyEncoder


class TestCustomModel(BaseTest):
    def setUp(self):
        super().setUp()

    def test_columns(self):
        table_info = {
            '__tablename__': 'sla_report',
            '__table_args__': {
                'autoload': False
            }
        }
        columns = {
            'string': Column('string', String(20)),
            'integer': Column('integer', Integer())
        }
        model = model_factory(columns, table_info)
        print(model)
        print(model.__base__)
        print(model.__tablename__)
        print(model.__table_args__)
        print(model.__table__.columns.keys())
        with TestCustomModel.app.app_context():
            conn = self.internal_connection(
                TestCustomModel.app.config['SQLALCHEMY_DATABASE_URI'],
                echo=TestCustomModel.app.config['SQLALCHEMY_ECHO'],
                cls=model
            )
            for x in range(5):
                conn.add(model())
            conn.commit()
            foo = conn.query(model).options().all()  # this lets you specify repr order
            print(foo)
        self.assertTrue(True)

    def test_identify_columns(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        all_call_data = self.example_data_src.example(datetime.today().date(), clients)
        # print(all_call_data[0])
        data = DataFrame(
            all_call_data
        )
        # data.set_index('call_id', inplace=True)
        print(data.dtypes)
        # print(data)
        # for call_id, call_data in all_call_data:
        #     print(call_id)
        #     encoded_data = dumps(call_data, cls=MyEncoder)
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
        #     data_src_records = [dict(zip(row.keys(), row)) for row in result]
        #     # print(data_src_records[0], flush=True)
        #     # record = data_src_records[0]
        #     # print(dumps(record, indent=4, cls=MyEncoder))
        #     data = DataFrame(
        #         data_src_records
        #     )
        #     data.set_index('call_id', inplace=True)
        #     # print(data.dtypes)
        #     # print(data)
        self.assertTrue(True)
