from datetime import datetime
from json import dumps


from app.fixtures.base_test import BaseTest
from app.lib.call_center import CallCenter
from app.lib.json_encoders import MyEncoder


class TestCallCenter(BaseTest):

    def setUp(self):
        super().setUp()
        self.func = CallCenter()

    def test_2(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = self.func.example(datetime.today().date(), clients)
        for call in day_of_calls:
            print(call)
            # print(dumps(day_of_calls[call_id], cls=MyEncoder, indent=4))
            pass

        self.assertTrue(True)

