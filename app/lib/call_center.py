from radar import random_datetime, randint
from datetime import timedelta, datetime, time
from math import pow, ceil


class Call:

    def __init__(self, client):
        self._receiving_party = client
        self.mod = randint(1, 20)   # Prevent divide by zero

    @property
    def receiving_party(self):
        return self._receiving_party

    # TODO this doesn't prevent a 0 in the first idx pos
    @property
    def calling_party(self):
        return ''.join(
            [
                str(
                    ceil(
                        (
                            x - randint(-9, 9)
                            * pow(-1, x)  # Oscillate
                        ) % 10  # only want integers 0-8
                    )
                ) for x in range(0, 10)      # Generate a std length phone number
            ]
        )

    @property
    def answered(self):
        return self.mod % 2 == 1

    @property
    def total_time(self):
        return timedelta(
            seconds=(
                (
                    pow(randint(0, 5) + self.mod, self.mod - randint(0, 5))
                ) % 900         # Ensure the time is reasonable ~ less than 15 minutes
            )
        )

    @property
    def talking_time(self):
        return timedelta(
            seconds=(1 / self.mod) * 900   # get some small and some large hold times
        ) if self.answered else timedelta(0)

    @property
    def wait_time(self):
        return self.total_time - self.talking_time

    @property
    def voice_mail(self):
        return False if self.answered else (
            pow(5 + self.mod, self.mod - 3) % 3
        ) == 2                  # could be a voice mail, but not too many


class CallCenter:

    @staticmethod
    def example(date, clients):
        # Use the date to seed our call_id -> we can run multiple examples w/o duplicate pk
        # This is roughshod right now
        call_id_seed = int(''.join(str(i) for i in (date.month, date.day, date.year)))
        calls = {}
        num_clients = len(clients)
        for index in range(num_clients*date.month*randint(1, 5)):
            call = Call(clients[(index - randint(0, 7)) % num_clients])
            start_time = random_datetime(
                start=datetime.combine(date, time(0)),
                stop=datetime.combine(date, time(hour=23, minute=59, second=59))
            )
            calls[start_time] = {
                'Start Time': start_time,
                'End Time': start_time + call.total_time,
                'Talking Duration': call.talking_time,
                'Hold Time': call.wait_time,
                'Unique Id2': call.calling_party,      # Calling party
                'Unique Id1': call.receiving_party,    # Receiving Party
                'Voice Mail': call.voice_mail,
                'Events': {},
                'Event Summary': {}
            }
        return {
            '{call_id}'.format(call_id=call_id_seed + index): calls[key] for index, key in enumerate(sorted(calls.keys()))
        }
