from flask import render_template, g, Blueprint, current_app
from pandas import DataFrame

from app.src.factory import get_page_args, get_pagination, internal_connection
from app.models.flexible_storage import FlexibleStorage

mod = Blueprint('index', __name__, template_folder='templates')


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


@mod.route('/')
def index():
    page, per_page, offset = get_page_args()
    # query = (
    #     g.db.query(FlexibleStorage)
    #     .order_by(FlexibleStorage.id.desc())
    #     .limit(per_page)
    #     .offset(offset)
    # ).all()
    # df = DataFrame.from_records([q.to_dict() for q in query])
    # if not df.empty:
    #     df.set_index(['call_id', 'event_id'], inplace=True)'
    if current_app.data_src.model('sla_report'):
        record_set = (
            g.db.query(current_app.data_src.model('sla_report'))
                .order_by(current_app.data_src.model('sla_report').id.desc())
                .limit(per_page)
                .offset(offset)
        ).all()
        df = DataFrame(
            [rec.to_dict() for rec in record_set]
        )
    else:
        record_set = []
        df = DataFrame()
    if not df.empty:  # Protect from KeyError if the dB is empty
        df.set_index('id', inplace=True)  # inplace = True saves us from having to bind a new dataframe
        # data.rename_axis(None)          # remove id label <- not working
        df.name = 'test'
        del df.index.name  # remove id label
        # print(df.datatypes)
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=len(record_set),
        record_name='id',
        format_total=True,
        format_number=True,
    )
    return render_template(
        'index.html',
        records=record_set,
        page=page,
        per_page=per_page,
        pagination=pagination,
        tables=[frame.to_html(classes='report') for frame in (df,) if not frame.empty],
        titles=['na', *[frame.name for frame in (df,) if not frame.empty]]
    )
