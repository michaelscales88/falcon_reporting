from flask import render_template, g, Blueprint, current_app


from app.src.factory import get_page_args, get_pagination
from app.models.flexible_storage import FlexibleStorage
from app.src.factory import internal_connection

mod = Blueprint('index', __name__, template_folder='templates')


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
