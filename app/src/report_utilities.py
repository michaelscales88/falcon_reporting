from datetime import datetime, date, time, timedelta
from dateutil.parser import parse
from pyexcel import Book, Sheet, get_book
from subprocess import Popen
from re import split

# from pywinauto.findwindows import find_window, WindowNotFoundError
# from pywinauto.controls.hwndwrapper import HwndWrapper

from .utility_base import UtilityBase


class ReportUtilities(UtilityBase):

    @staticmethod
    def is_weekday(given_day):
        try:
            return ReportUtilities.day_of_week(given_day) not in (5, 6)
        except AttributeError:
            print('{date} is invalid to get day of the week.'.format(date=given_day))

    @staticmethod
    def day_of_week(given_day):
        return given_day.weekday() if isinstance(given_day, (datetime, date)) else 'Unknown Date'

    @staticmethod
    def name_of_day(given_day):
        return given_day.strftime('%A') if isinstance(given_day, (datetime, date)) else 'Unknown Date'

    @staticmethod
    def date_to_dt(raw_date):
        return datetime.combine(raw_date, time()) if isinstance(raw_date, date) else raw_date

    @staticmethod
    def phone_number(mixed_string):
        only_digits = [ch for ch in str(mixed_string) if ch.isdigit()]
        try:
            return int(
                str(
                    ''.join(
                        only_digits[1:]
                        if len(only_digits) > 7 and only_digits[0] == 1
                        else only_digits
                    )
                )
            )
        except ValueError:
            return None

    @staticmethod
    def find_non_distinct(sheet=None, event_col=None):
        i_count = {}
        for row_name in reversed(sheet.rownames):
            dup_event = sheet[row_name, event_col]
            dup_info = i_count.get(
                dup_event, {
                    'count': 0,
                    'rows': []
                }
            )
            dup_info['count'] += 1
            dup_info['rows'].append(row_name)
            i_count[dup_event] = dup_info
        return i_count

    @staticmethod
    def datetime_handler(x):
        # print(type(x))
        if isinstance(x, datetime):
            return x.isoformat()
        elif isinstance(x, timedelta):
            return str(x)
        else:
            return str(x)
        # raise TypeError("Unknown type")

    @staticmethod
    def to_td(v):
        try:
            v = timedelta(seconds=ReportUtilities.get_sec(v))
        except (AttributeError, ValueError) as e:
            print(e, v)
        return v

    @staticmethod
    def to_dt(v):
        try:
            v = parse(v)
        except (AttributeError, ValueError) as e:
            print(e, v)
        return v

    @staticmethod
    def valid_dt(date_string):
        validated_dt = None
        try:
            validated_dt = parse(date_string, ignoretz=True)
        except ValueError:
            pass
        return validated_dt

    @staticmethod
    def shortest_longest(*args):
        return (args[0], args[1]) if args[0] is min(*args, key=len) else (args[1], args[0])

    @staticmethod
    def return_selection(input_opt):
        selection = list(input_opt.values())
        return selection[
            int(
                input(
                    ''.join(['{k}: {i}\n'.format(k=k, i=i) for i, k in enumerate(input_opt)])
                )
            )
        ]

    @staticmethod
    def find(lst, a):
        return [i for i, x in enumerate(lst) if x == a]

    @staticmethod
    def is_empty_wb(book):
        if isinstance(book, Book):
            return book.number_of_sheets() is 0

    @staticmethod
    def make_summary(headers):
        todays_summary = Sheet()
        todays_summary.row += headers
        todays_summary.name_columns_by_row(0)
        return todays_summary

    # TODO consider methods like this to move into UtilityObject
    @staticmethod
    def add_time(dt_t, add_time=None):
        return (datetime.combine(datetime.today(), dt_t) + add_time).time()

    @staticmethod
    def safe_parse(dt=None):
        try:
            return parse(dt)
        except ValueError:
            print('Could not parse date_time: {dt}'.format(dt=dt))

    # TODO this need to be able to handle more data types than excel
    # TODO 2: this should also download files
    @staticmethod
    def load_data(report):
        print('testing load_data')

    @staticmethod
    def safe_div(num, denom):
        rtn_val = 0
        try:
            rtn_val = num / denom
        except ZeroDivisionError:
            pass
        return rtn_val

    # Generator Section
    @staticmethod
    def common_keys(*dcts):
        for i in set(dcts[0]).intersection(*dcts[1:]):
            yield (i,) + tuple(d[i] for d in dcts)

    @staticmethod
    def return_matches(*args, match_val=None):
        if len(args) == 2:
            shortest_list, longest_list = ReportUtilities.shortest_longest(*args)
            longest_list_indexed = {}
            for item in longest_list:
                longest_list_indexed[item[match_val]] = item
            for item in shortest_list:
                if item[match_val] in longest_list_indexed:
                    yield item, longest_list_indexed[item[match_val]]

    @staticmethod
    def open_focus(target, p_type='explorer'):
        try:
            HwndWrapper(find_window(title=ReportUtilities.base(target))).set_focus()
        except WindowNotFoundError:
            Popen('{process} "{path}"'.format(
                process=p_type,
                path=target)
            )
        except FileNotFoundError:
            print('File: {target} does not exist.'.format(target=target))

    @staticmethod
    def open_directory(tgt_dir):
        ReportUtilities.open_focus(tgt_dir)
        input('Any key to continue.')

    @staticmethod
    def start(full_path):
        ReportUtilities.open_focus(full_path)


