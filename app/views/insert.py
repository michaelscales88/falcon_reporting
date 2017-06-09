from flask import render_template, current_app, Blueprint, g, redirect, url_for


from app.src.factory import get_page_args, get_pagination, query_statement, internal_connection
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
    src, records = query_statement(
        current_app.config['TEST_STATEMENT'],
        current_app.config['EXTERNAL_CONNECTION']
    )
    data_src_records = [dict(zip(row.keys(), row)) for row in records]
    current_app.data_src.insert_records('sla_report', data_src_records)
    return show_inserted([rec.id for rec in records])


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
    return show_inserted([i for i in range(len(records))])


def show_inserted(ids):
    page, per_page, offset = get_page_args()
    record_set = current_app.data_src.get_records(
        'sla_report',
        offset=offset,
        ids=ids,
        per_page=per_page
    )
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

# Dis is how i dougie with Blueprints
# mod.add_url_rule('/insert/hello/', view_func=DataFrameView.as_view('hello'))
