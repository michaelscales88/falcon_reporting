import unittest


class TestLoader(unittest.TestCase):

    def test_call_center_test(self):
        from datetime import datetime
        from app import lib
        clients = ['Susy', 'Josh', 'Sally', 'Emily']
        day_of_calls = lib.call_center.CallCenter().example(datetime.today().date(), clients)
        for call_id in sorted(day_of_calls.keys()):
            print(call_id, day_of_calls[call_id])
            return call_id, day_of_calls[call_id]


if __name__ == '__main__':
    unittest.main()
