from radar import random_datetime, randint
from datetime import timedelta, datetime, time
from math import pow, ceil


def event_generator(call, call_time, call_id, event_id):
    """
    # 1 ringing
    # 4 Talking
    # 5 Hold
    # 6 Other Hold
    # 7 other other hold
    # 10 voice mail
    # 21 call drop
    """
    events = []
    call_duration = call.total_time
    if call.answered:
        while call_duration > timedelta(0):
            event = {

            }
            call_duration -= timedelta(60)
            events.append(event)
    else:
        events.append(
            {
                'event_id': event_id,
                'call_id': call_id,
                'Start Time': call_time,
                'End Time': call_time + call.total_time,
                'event_type': 1
            }
        )
        event_id += 1
        if call.voice_mail:
            events.append(
                {
                    'event_id': event_id,
                    'call_id': call_id,
                    'Start Time': call_time + call.total_time,
                    'End Time': call_time + call.total_time,
                    'event_type': 10
                }
            )
            event_id += 1
        events.append(
            {
                'event_id': event_id,
                'call_id': call_id,
                'Start Time': call_time + call.total_time,
                'End Time': call_time + call.total_time,
                'event_type': 21
            }
        )
        event_id += 1
        call_id += 1
    return events


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
        call_id = int(''.join(str(i) for i in (date.month, date.day, date.year)))   # seed the first call_id
        event_id = call_id * 10                                                     # # events > # of calls
        call_time = random_datetime(                                                # seed the first call of the day
            start=datetime.combine(date, time(0)),
            stop=datetime.combine(date, time(hour=23, minute=59, second=59))
        )
        calls = []
        num_clients = len(clients)
        for index in range(num_clients*date.month*randint(1, 5)):       # create randomish number of calls
            call = Call(clients[(index - randint(0, 7)) % num_clients])
            events = event_generator(call, call_time, call_id, event_id)


            # calls[start_time] = {
            #     'Start Time': start_time,
            #     'End Time': start_time + call.total_time,
            #     'Talking Duration': call.talking_time,
            #     'Hold Time': call.wait_time,
            #     'Unique Id2': call.calling_party,      # Calling party
            #     'Unique Id1': call.receiving_party,    # Receiving Party
            #     'Voice Mail': call.voice_mail,
            #     'Events': {
            #         # 'dummy_key{}'.format(start_time): 'This information is being simulated in event summary'
            #     },
            #     'Event Summary': {
            #         '4': call.talking_time,                 # Talking Time
            #         '10': timedelta(randint(15, 300)) if call.voice_mail else timedelta(0),  # Voice mail
            #         '5': call.wait_time,                    # Hold time
            #         '6': timedelta(0),                      # Hold time
            #         '7': timedelta(0)                       # Hold time
            #     }
            # }
            calls.extend(events)   # grow in place
        return calls
