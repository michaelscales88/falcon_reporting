import unittest
from falcon_reporting.app.lib.call_center import CallCenter
from datetime import timedelta, datetime
from json import dumps, JSONEncoder
from decimal import Decimal


class MyEncoder(JSONEncoder):
    """Convert non-serializable data into a value which we can store in our dB"""
    def default(self, obj):
        if isinstance(obj, (datetime,)):
            return {"val": obj.isoformat(), "_spec_type": "datetime"}
        elif isinstance(obj, (Decimal,)):
            return {"val": str(obj), "_spec_type": "decimal"}
        elif isinstance(obj, (timedelta,)):
            return {"val": str(obj), "_spec_type": "timedelta"}
        else:
            return super().default(obj)


class TestCallCenter(unittest.TestCase):
    def setUp(self):
        self.func = CallCenter()

    def test_1(self):
        self.assertTrue(True)

    def test_2(self):
        self.assertTrue(True)

    def test_3(self):
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = self.func.example(datetime.today().date(), clients)
        for call_id in sorted(day_of_calls.keys()):
            print(call_id)
            print(dumps(day_of_calls[call_id], cls=MyEncoder, indent=4))


if __name__ == '__main__':
    unittest.main()
