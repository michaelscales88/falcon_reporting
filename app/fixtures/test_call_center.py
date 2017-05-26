import unittest
from datetime import datetime
from json import dumps
from falcon_reporting.app import app

from falcon_reporting.app.lib.call_center import CallCenter
from falcon_reporting.app.lib.json_encoders import MyEncoder


class TestCallCenter(unittest.TestCase):
    app = app

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + ':memory:'
        # self.app = app.test_client()
        self.func = CallCenter()
        # db.create_all()

    def tearDown(self):
        # db.session.remove()
        # db.drop_all()
        pass

    def test_1(self):
        self.assertTrue(True)

    def test_2(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = self.func.example(datetime.today().date(), clients)
        for call_id in sorted(day_of_calls.keys()):
            print(call_id)
            print(dumps(day_of_calls[call_id], cls=MyEncoder, indent=4))

        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
