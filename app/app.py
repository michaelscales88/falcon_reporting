from click import command, option
from flask import Flask, render_template, g, current_app
from sqlalchemy import func
from datetime import datetime, timedelta
from random import randint, sample, randrange
from math import ceil
from radar import random_datetime, utils as radar_parse


from app.src.factory import (
data_src, internal_connection, query_statement
)
from app.db_models.flexible_storage import FlexibleStorage
from app.tests.test_internal_storage import cache
from . import get_page_args, Pagination
from app.tests.report_test import report

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

_connection = 'postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'
_test_date = datetime.today().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0)

statement = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '{}' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''.format(_test_date.strftime('%Y-%M-%D'))


@app.before_request
def before_request():
    # Set up our dB connection for pagination
    g.session = internal_connection(app.config['SQLALCHEMY_DATABASE_URI'], echo=True, cls=FlexibleStorage)


@app.teardown_request
def teardown(error):
    # Close out whatever for the app to exit
    g.session.close()


@app.route('/')
def index():
    total_records = g.session.query(FlexibleStorage).count()
    page, per_page, offset = get_page_args()
    record_set = g.session.query(FlexibleStorage).order_by(FlexibleStorage.id).slice(per_page, offset).all()
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total_records,
        record_name='id',
        format_total=True,
        format_number=True,
    )
    return render_template(
        'index.html',
        users=record_set,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route('/init_db')
def init_db():
    src, result = query_statement(statement, _connection)  # Make a connection to the PG dB and execute the query
    data_src_records = [dict(zip(row.keys(), row)) for row in result]
    cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
    for pk, call_data_dict in cached_records.items():
        call_data = FlexibleStorage(
            id=pk,
            start=call_data_dict.pop('Start Time'),
            end=call_data_dict.pop('End Time'),
            unique_id1=call_data_dict.pop('Unique Id1'),
            unique_id2=call_data_dict.pop('Unique Id2'),
            data=call_data_dict
        )
        g.session.add(call_data)
    g.session.commit()
    return 'Added {number} records to the database'.format(number=len(cached_records))


@app.route('/test_db')
def test_db():
    small_to_big = [call_id for call_id in range(2000)]
    big_to_small = [call_id for call_id in reversed(small_to_big)]
    half_small_to_big = [ceil(call_id*.5) for call_id in small_to_big]
    for pk, bts, stb in zip(small_to_big, big_to_small, half_small_to_big):
        call_start = random_datetime(start='2012-05-24T00:00:00', stop='2013-05-24T23:59:59', parse=radar_parse.parse)
        call_data_dict = {
            'Start Time': call_start,
            'End Time': (
                call_start
                + timedelta(seconds=ceil(randint(0, bts) * .8))
                - timedelta(seconds=ceil(randint(0, stb) * .5))
            ),
            'Unique Id1': ceil(
                (pk * bts + bts * pk + stb * bts)
                / 2
            ),
            'Unique Id2': ceil(
                (pk * (bts * 4) + pk * 5 + stb * stb)
                * 2
                / 4
            ),
            'Events': {
                'Lots{}'.format(bts): 'of{} stuff'.format(stb),
                'to See': 'here{}'.format(bts+stb)
            }

        }
        call_data = FlexibleStorage(
            id=pk,
            start=call_data_dict.pop('Start Time'),
            end=call_data_dict.pop('End Time'),
            unique_id1=call_data_dict.pop('Unique Id1'),
            unique_id2=call_data_dict.pop('Unique Id2'),
            data=call_data_dict
        )
        g.session.add(call_data)
    g.session.commit()
    # print(call_ids)
    return '\n'.join([str(call_id) for call_id in small_to_big])


@app.route('/run_report')
def run_report():
    return str(
        report(
            g.session.query(FlexibleStorage).filter(func.date(_test_date)).all()
        )
    )


def get_css_framework():
    return current_app.config.get('CSS_FRAMEWORK', 'bootstrap3')


def get_link_size():
    return current_app.config.get('LINK_SIZE', 'sm')


def show_single_page_or_not():
    return current_app.config.get('SHOW_SINGLE_PAGE', False)


def get_pagination(**kwargs):
    kwargs.setdefault('record_name', 'records')
    return Pagination(css_framework=get_css_framework(),
                      link_size=get_link_size(),
                      show_single_page=show_single_page_or_not(),
                      **kwargs
                      )


@command()
@option('--port', '-p', default=5000, help='listening port')
def run(port):
    app.run(host='0.0.0.0', debug=True, port=port)

if __name__ == '__main__':
    run()
