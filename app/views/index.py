from flask import render_template, g, Blueprint


from app.src.factory import get_page_args, get_pagination
from app.models.flexible_storage import FlexibleStorage

mod = Blueprint('index', __name__, template_folder='templates')


@mod.route('/')
def index():
    page, per_page, offset = get_page_args()
    record_set = (
        g.db.query(FlexibleStorage)
        .order_by(FlexibleStorage.id.desc())
        .limit(per_page)
        .offset(offset)
    ).all()
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
        users=record_set,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )
