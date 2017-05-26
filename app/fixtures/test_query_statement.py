from pandas import DataFrame
from falcon_reporting.app.fixtures.base_test import BaseTest
from falcon_reporting.app.src.factory import query_statement, internal_connection
from falcon_reporting.app.lib.sla_cache import cache
from falcon_reporting.app.models.flexible_storage import FlexibleStorage


class TestQueryStatement(BaseTest):

    def setUp(self):
        super().setUp()
        self.query_func = query_statement
        self.internal_connection = internal_connection(
            TestQueryStatement.app.config['SQLALCHEMY_DATABASE_URI'],
            echo=TestQueryStatement.app.config['SQLALCHEMY_ECHO'],
            cls=FlexibleStorage
        )
        src, result = self.query_func(
            TestQueryStatement.app.config['TEST_STATEMENT'],
            TestQueryStatement.app.config['EXTERNAL_CONNECTION']
        )
        self.data_src_records = [dict(zip(row.keys(), row)) for row in result]
        self.cached_records = cache(self.data_src_records, pk='call_id', subkey='event_id')

    def test_1(self):
        for pk, call_data_dict in self.cached_records.items():
            call_data = FlexibleStorage(
                id=pk,
                start=call_data_dict.pop('Start Time'),
                end=call_data_dict.pop('End Time'),
                unique_id1=call_data_dict.pop('Unique Id1'),
                unique_id2=call_data_dict.pop('Unique Id2'),
                data=call_data_dict
            )
            self.internal_connection.add(call_data)
        self.internal_connection.commit()
        self.assertTrue(True)

    def test_2(self):
        per_page = 10
        offset = 0
        record_set = (
            self.internal_connection.query(FlexibleStorage)
                .order_by(FlexibleStorage.id.desc())
                .limit(per_page)
                .offset(offset)
        ).all()
        print(len(record_set), type(record_set))
        print(len(record_set), type(record_set))
        data = DataFrame(
            [rec.to_dict() for rec in record_set]
        )
        data.set_index('id', inplace=True)      # inplace = True saves us from having to bind a new frame
        # data.rename_axis(None, inplace=True)  # this doesn't work
        del data.index.name
        print(data)
        self.assertTrue(True)
