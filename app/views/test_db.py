from flask import render_template, g, Blueprint
from radar import random_datetime, utils as radar_parse
from random import randint, sample, randrange
from math import ceil
from datetime import datetime, timedelta

from app.src.factory import get_page_args, get_pagination, query_statement
from app.tests.test_internal_storage import cache
from app.db_models.flexible_storage import FlexibleStorage

mod = Blueprint('test_db', __name__)


@mod.route('/test_db/')
@mod.route('/test_db')
def test_db():
    small_to_big = [call_id for call_id in range(2000)]
    big_to_small = [call_id for call_id in reversed(small_to_big)]
    half_small_to_big = [ceil(call_id*.5) for call_id in small_to_big]
    for pk, bts, stb in zip(small_to_big, big_to_small, half_small_to_big):
        call_start = random_datetime(start='2012-05-01T00:00:00', stop='2013-05-01T23:59:59', parse=radar_parse.parse)
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
    # return render_template('index.html',
    #                        users=record_set,
    #                        page=page,
    #                        per_page=per_page,
    #                        pagination=pagination,
    #                        active_url='records-page-url',
    #                        )