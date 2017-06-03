from datetime import datetime, timedelta, time
from math import ceil

from flask import render_template, current_app, Blueprint, g, redirect, url_for
from radar import random_datetime
from random import randint


from app.models.flexible_storage import FlexibleStorage
from app.src.factory import get_page_args, get_pagination, query_statement, model_factory, internal_connection
from app.lib.sla_cache import cache
from app.lib.call_center import CallCenter

mod = Blueprint('insert', __name__, template_folder='templates')


@mod.before_request
def before_request():
    # Set up our dB connection
    model = current_app.data_src.model('sla_report')
    if model:
        g.db = internal_connection(
            current_app.config['SQLALCHEMY_DATABASE_URI'],
            echo=current_app.config['SQLALCHEMY_ECHO'],
            cls=model
        )


@mod.route('/init_db/')
@mod.route('/init_db')
def init_db():
    # Make a connection to the PG dB and execute the query
    src, result = query_statement(current_app.config['TEST_STATEMENT'], current_app.config['EXTERNAL_CONNECTION'])
    data_src_records = [dict(zip(row.keys(), row)) for row in result]
    cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
    return insert_records(cached_records)


@mod.route('/init_db2/')
@mod.route('/init_db2')
def init_db2():
    # Make a connection to the PG dB and execute the query
    src, result = query_statement(current_app.config['TEST_STATEMENT'], current_app.config['EXTERNAL_CONNECTION'])
    model, data = model_factory(result)
    # data_src_records = [dict(zip(row.keys(), row)) for row in result]
    # cached_records = cache(data_src_records, pk='call_id', subkey='event_id')
    return insert_records(data, model=model)


@mod.route('/test_db/')
@mod.route('/test_db')
def test_db():
    # Sample data from app/lib/call_center.py
    records = CallCenter().example(
        current_app.test_date,
        list(current_app.config['CLIENTS'])
    )
    name = 'sla_report'
    current_app.data_src.insert_records(name, records)
    print('inserted records and found model', current_app.data_src.model(name))
    return show_inserted([i for i in range(30000)], model=current_app.data_src.model(name))


def insert_records(records):
    for pk, call_data_dict in records.items():
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
    return show_inserted(records.keys(), model=FlexibleStorage)


def insert_records2(name, records):
    for pk, call_data_dict in records.items():
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
    return show_inserted(records.keys())


def show_inserted(ids, model=None):
    page, per_page, offset = get_page_args()
    print(page, per_page, offset)
    record_set = current_app.data_src.get_records('sla_report', offset=offset, ids=ids)
    # if current_app.data_src.model('sla_report'):
    #     record_set = (
    #         g.db.query(model)
    #         .order_by(model.id)
    #         .filter(model.id.in_(ids))
    #         .limit(per_page)
    #         .offset(offset)
    #         .all()
    #     )
    # else:
    #     record_set = []
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=len(ids),
        record_name='records',
        format_total=True,
        format_number=True
    )
    return render_template(
        'insert.html',
        records=record_set,
        total=pagination.total,
        pagination=pagination,
        page=page,
        per_page=per_page,
        active_url='insert-test_db-url',
    )
