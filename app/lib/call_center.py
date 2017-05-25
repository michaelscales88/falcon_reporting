from radar import random_datetime, randint
from datetime import timedelta, datetime, time
from math import pow, ceil


class Call:

    def __init__(self, client, seed):
        self._receiving_party = client
        self.mod = seed + 1     # Prevent divide by zero

    @property
    def receiving_party(self):
        return self.receiving_party

    @property
    def calling_party(self):
        return ''.join(
            [
              str(
                  (
                      (
                          (x + self.mod)  # Mix it up
                          * pow(-x, x)    # Oscillate
                      ) % 10              # only want integers 0-9
                  )
              ) for x in range(0, 7)      # Generate a std length phone number
            ]
        )

    @property
    def answered(self):
        return not (
            (self.mod * 3) % 2
        )

    @property
    def total_time(self):
        return timedelta(
            seconds=(
                (
                    pow(5 + self.mod, self.mod - 3)
                ) % 900         # Ensure the time is reasonable ~ less than 15 minutes
            )
        )

    @property
    def talking_time(self):
        return timedelta(0) if self.answered else timedelta(
            seconds=(1 / self.mod) * 900   # get some small and some large hold times
        )

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
        calls = {}
        num_clients = len(clients)
        for index in range(num_clients*date.month()*randint(1, 5)):
            seed = int(
                date.year() % (
                    ceil(
                        index /
                        (date.month() * date.day())
                    ) * 10
                )
            )
            call = Call(clients[(index - randint(0, 7)) % num_clients], seed)
            start_time = random_datetime(
                start=datetime.combine(date, time(0)),
                stop=datetime.combine(date, time(hour=23, minute=59, second=59))
            )
            calls[start_time] = {
                'Start Time': start_time,
                'End Time': start_time + call.total_time,
                'Talking Duration': call.talking_time,
                'Hold Time': call.wait_time,
                'Calling Party': call.calling_party,
                'Receiving Party': call.receiving_party,
                'Voice Mail': call.voice_mail
            }
        return {
            '{call_id}'.format(call_id=index): the_dict for index, k, the_dict in enumerate(sorted(calls.items()))
        }


