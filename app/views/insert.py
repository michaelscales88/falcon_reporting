from flask import render_template, current_app, Blueprint, g
from radar import random_datetime, utils as radar_parse
from random import randint, sample, randrange
from math import ceil
from datetime import datetime, timedelta, time

from app.tests.test_internal_storage import cache
from app.src.factory import get_page_args, get_pagination, query_statement
from app.models.flexible_storage import FlexibleStorage
from app.src.factory import internal_connection

mod = Blueprint('insert', __name__, template_folder='templates')


@mod.before_request
def before_request():
    # Set up our dB connection
    g.db = internal_connection(
        current_app.config['SQLALCHEMY_DATABASE_URI'],
        echo=current_app.config['SQLALCHEMY_ECHO'],
        cls=FlexibleStorage
    )


@mod.teardown_request
def teardown(error):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@mod.route('/init_db/')
@mod.route('/init_db')
def init_db():
    # Make a connection to the PG dB and execute the query
    src, result = query_statement(current_app.statement, current_app.connection)
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
        g.db.add(call_data)
    g.db.commit()
    return inserted(cached_records.keys())


@mod.route('/test_db/')
@mod.route('/test_db')
def test_db():
    small_to_big = [call_id for call_id in range(2000)]
    big_to_small = [call_id for call_id in reversed(small_to_big)]
    half_small_to_big = [ceil(call_id*.5) for call_id in small_to_big]
    start_dt = datetime.combine(current_app.test_date, time(0))
    end_dt = datetime.combine(current_app.test_date, time(hour=23, minute=59, second=59))
    for pk, bts, stb in zip(small_to_big, big_to_small, half_small_to_big):
        # call_start = random_datetime(start='2012-05-01T00:00:00', stop='2013-05-01T23:59:59', parse=radar_parse.parse)
        call_start = random_datetime(
            start=start_dt,
            stop=end_dt
        )
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
    return inserted(small_to_big)


def inserted(ids):
    record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).filter(FlexibleStorage.id.in_(ids))
    page, per_page, offset = get_page_args()
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=len(ids),
        record_name='users',
        format_total=True,
        format_number=True
    )
    return render_template(
        'insert.html',
        users=record_set,
        total=pagination.total,
        pagination=pagination,
        page=page,
        per_page=per_page,
        active_url='insert-test_db-url',
    )
