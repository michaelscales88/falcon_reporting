#!/Users/michaelscales/Desktop/local/environments/flask_venv/bin/python3.5
from datetime import datetime
from json import dumps
from platform import system
from os import chdir

if system() in ('Darwin', 'Linux'):
    from app.fixtures.base_test import BaseTest
    from app.lib.call_center import CallCenter
    from app.lib.json_encoders import MyEncoder
else:
    from falcon_reporting.app.fixtures.base_test import BaseTest
    from falcon_reporting.app.lib.call_center import CallCenter
    from falcon_reporting.app.lib.json_encoders import MyEncoder


class TestCallCenter(BaseTest):

    def setUp(self):
        super().setUp()
        self.func = CallCenter()

    def test_2(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = self.func.example(datetime.today().date(), clients)
        for call_id in sorted(day_of_calls.keys()):
            # print(call_id)
            # print(dumps(day_of_calls[call_id], cls=MyEncoder, indent=4))
            pass

        self.assertTrue(True)

