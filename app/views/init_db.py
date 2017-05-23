from flask import render_template, current_app, Blueprint

from app.src.factory import get_page_args, get_pagination, query_statement
from app.tests.test_internal_storage import cache
from app.db_models.flexible_storage import FlexibleStorage

mod = Blueprint('init_db', __name__)


@mod.route('/init_db/')
@mod.route('/init_db')
def init_db():
    src, result = query_statement(current_app.statement, current_app.connection)  # Make a connection to the PG dB and execute the query
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
    # return render_template('index.html',
    #                        users=record_set,
    #                        page=page,
    #                        per_page=per_page,
    #                        pagination=pagination,
    #                        active_url='records-page-url',
    #                        )