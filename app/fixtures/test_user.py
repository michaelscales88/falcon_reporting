from datetime import datetime
from json import dumps

from app.fixtures.base_test import BaseTest
from app.report.src.call_center import CallCenter


class TestCallCenter(BaseTest):

    def setUp(self):
        super().setUp()
        self.func = CallCenter()

    def test_2(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = self.func.example(datetime.today().date(), clients)
        for call in day_of_calls:
            # print(call['start_time'], type(call['start_time']))
            print(dumps(call, indent=4, default=str))
            pass

        self.assertTrue(True)

    def test_3(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        result = self.func.example(datetime.today().date(), clients)
        print(result)
        data_src_records = [dict(zip(row.keys(), row)) for row in result]
        # for call in data_src_records:
        #     print(call)
        cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
        self.assertTrue(True)
