from radar import random_datetime
from datetime import timedelta
from math import pow


class Call:

    def __init__(self, client, seed):
        self.receiving_party = client
        self._mod = seed

    @property
    def incoming_party(self):
        return ''.join(
            [
              str(
                  (
                      (
                          (x + self._mod)   # Mix it up
                          * pow(-1, x)
                      ) % 10                # only want integers 0-9
                  )
              ) for x in range(0, 7)        # Generate a std length phone number
            ]
        )

    @property
    def answered(self):
        return not (
            (self._mod * 3) % 2
        )

    @property
    def total_time(self):
        return timedelta(
            seconds=(
                (
                    pow(5 + self._mod, self._mod - 3)
                ) % 900     # Ensure the time is reasonable ~ less than 15 minutes
            )
        )

    @property
    def hold_time(self):
        return timedelta(
            seconds=(
                (
                    pow(5 + self._mod, self._mod - 3)
                ) % (
                    (1 / self._mod) * 900   # get some small and some large hold times
                )
            )
        )

    @property
    def wait_time(self):
        return self.total_time - self.hold_time

    @property
    def voice_mail(self):
        return True if self.answered else (
            pow(5 + self._mod, self._mod - 3) % 5
        ) == 2  # could be a voice mail, but not too many


class CallCenter:

    @staticmethod
    def example(date):
        seed = int(
            date.year() % (
                date.month() * date.day()
            )
        )
        return {}

    @staticmethod
    def date_time(date, seed):
        return random_datetime(
            start=date
        )

