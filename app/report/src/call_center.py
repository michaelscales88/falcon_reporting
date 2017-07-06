from radar import random_datetime, randint
from datetime import timedelta, datetime, time
from math import pow, ceil


class EventManager:

    event_id = None
    call_id = None

    @staticmethod
    def increment_time(event_cursor, start, end, time_value):
        if event_cursor[end]:   # catch the first increment since end is none
            event_cursor[start] = event_cursor[end]
        event_cursor[end] = event_cursor[start] + time_value

    @staticmethod
    def increment(event_cursor, value, inc):
        try:
            event_cursor[value] += inc
        except TypeError:
            print('cant add those types')

    # @staticmethod
    # def thread_events(event_cursor, call, events):
    #     for event_type, event_time in call.call_flow():
    #         event_manager.increment_time(event_cursor, 'start_time', 'end_time', event_time)
    #         event = {
    #             'event_id': EventManager.event_id,
    #             'start_time': event_cursor['start_time'],
    #             'end_time': event_cursor['end_time'],
    #             'call_id': EventManager.call_id,
    #             'calling_party_number': call.calling_party,  # Calling party
    #             'dialed_party_number': call.receiving_party,  # Receiving Party
    #             'event_type': event_type
    #         }
    #         event_manager.increment(EventManager.event_id, 1)  # prepare for next event
    #         events.append(event)
    #     event_manager.increment(EventManager.call_id, 1)

event_manager = EventManager()


def event_generator(call, event_cursor):
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
    # currently this overflows on the day -> need some thread like mechanism for adding events concurrently
    for event_type, event_time in call.call_flow():
        event_manager.increment_time(event_cursor, 'start_time', 'end_time', event_time)
        event = {
            'event_id': event_cursor['event_id'],
            'start_time': event_cursor['start_time'],
            'end_time': event_cursor['end_time'],
            'call_id': event_cursor['call_id'],
            'calling_party_number': call.calling_party,      # Calling party
            'dialed_party_number': call.receiving_party,    # Receiving Party
            'event_type': event_type
        }
        event_manager.increment(event_cursor, 'event_id', 1)    # prepare for next event
        events.append(event)
    event_manager.increment(event_cursor, 'call_id', 1)         # prepare next call_id which is also new event
    return events


class Call:
    # TODO a to_dict fn would make this easy
    def __init__(self, client):
        self._receiving_party = client
        self.mod = randint(1, 20)   # Prevent divide by zero
        self._calling_party = ''.join(
            [
                str(
                    ceil(
                        (
                            x - randint(-self.mod, self.mod)
                            * pow(-1, x)  # Oscillate
                        ) % 9  # 0-8
                    ) + 1      # gives an integer 0-9
                ) for x in range(0, 10)      # Generate a 10 character phone number
            ]
        )

    @property
    def receiving_party(self):
        return self._receiving_party

    @property
    def calling_party(self):
        return self._calling_party

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
        ) == 2       # could be a voice mail, but not too many

    def call_flow(self):
        # this is where I can split up talk times, add conf, etc
        this_flow = [(1, self.wait_time)]
        if self.answered:
            this_flow.append(
                (4, self.talking_time)
            )
        elif self.voice_mail:
            this_flow.append(
                (10, timedelta(seconds=randint(15, 65)))
            )
        this_flow.append(
            (21, timedelta(0))
        )
        for item in this_flow:
            yield item


class CallCenter:

    @staticmethod
    def example(date, clients):
        # Use the date to seed our call_id -> we can run multiple examples w/o duplicate pk
        # This is roughshod right now
        call_id = int(''.join(str(i) for i in (date.month, date.day, date.year)))   # seed the first call_id
        call_time = random_datetime(                                                # seed the first call of the day
            start=datetime.combine(date, time(0)),
            stop=datetime.combine(date, time(hour=23, minute=59, second=59))
        )
        calls = []
        num_clients = len(clients)
        clients = list(clients)
        event_cursor = {
            'call_id': call_id,
            'event_id': call_id * 10,       # events > # of calls
            'start_time': call_time,
            'end_time': None

        }
        for index in range(num_clients*date.month*randint(1, 5)):       # create randomish number of calls
            call = Call(clients[(index - randint(0, 7)) % num_clients])
            events = event_generator(call, event_cursor)
            calls.extend(events)   # grow in place
        return calls
