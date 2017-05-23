from flask import render_template, g, Blueprint

from app.src.factory import get_page_args, get_pagination
from app.models.flexible_storage import FlexibleStorage

mod = Blueprint('records', __name__)


@mod.route('/records/', defaults={'page': 1})
@mod.route('/records', defaults={'page': 1})
@mod.route('/records/page/<int:page>/')
@mod.route('/records/page/<int:page>')
def records(page):
    total_records = g.session.query(FlexibleStorage).count()
    page, per_page, offset = get_page_args()
    record_set = g.session.query(FlexibleStorage).order_by(FlexibleStorage.id).limit(per_page).offset(offset).all()
    pagination = get_pagination(
        page=page,
        per_page=per_page,
        total=total_records,
        record_name='users',
        format_total=True,
        format_number=True
    )
    return render_template(
        'insert.html',
        users=record_set,
        page=page,
        per_page=per_page,
        pagination=pagination,
        active_url='records-page-url'
    )
