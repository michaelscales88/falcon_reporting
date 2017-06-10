from flask import render_template, g, Blueprint, current_app, request

from app.src.factory import get_page_args, get_pagination, internal_connection

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
    print(request)
    page, per_page, offset = get_page_args()
    total_records = current_app.data_src.record_count('sla_report')
    frame = current_app.data_src.page_view('sla_report', offset=offset, per_page=per_page)
    frame.name = 'default'
    try:
        frame.set_index(['event_id'], inplace=True)  # inplace = True saves us from having to bind a new dataframe
    except KeyError:
        pass
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
        page=page,
        per_page=per_page,
        pagination=pagination,
        tables=[fr.to_html(classes='report') for fr in (frame,) if not fr.empty],
        titles=['na', tuple(fr.name for fr in (frame,) if not fr.empty)],
        buttons=[col for col in list(frame)],
        active_btns=[]
    )
