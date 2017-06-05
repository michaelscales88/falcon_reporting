from flask import render_template, g, Blueprint, current_app


from app.src.factory import get_page_args, get_pagination
from app.models.flexible_storage import FlexibleStorage

mod = Blueprint('records', __name__, template_folder='templates')


@mod.route('/records/', defaults={'page': 1})
@mod.route('/records', defaults={'page': 1})
@mod.route('/records/page/<int:page>/')
@mod.route('/records/page/<int:page>')
def records(page):
    # total_records = g.db.query(FlexibleStorage).count()
    total_records = current_app.data_src.record_count('sla_report')
    page, per_page, offset = get_page_args()
    # record_set = g.db.query(FlexibleStorage).order_by(FlexibleStorage.id).limit(per_page).offset(offset).all()
    record_set = current_app.data_src.get_records('sla_report', offset=offset, per_page=per_page)
    df = current_app.data_src.get_frame('sla_report', offset=offset, per_page=per_page)
    df.set_index(['call_id', 'event_id'], inplace=True)
    print(df)
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total_records,
        record_name='records',
        format_total=True,
        format_number=True
    )
    return render_template(
        'index.html',
        records=record_set,
        page=page,
        per_page=per_page,
        pagination=pagination,
        active_url='records-page-url'
    )
