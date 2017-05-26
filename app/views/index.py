from flask import render_template, g, Blueprint
from pandas import DataFrame


from falcon_reporting.app.src.factory import get_page_args, get_pagination
from falcon_reporting.app.models.flexible_storage import FlexibleStorage

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
    df = DataFrame(
        [rec.to_dict() for rec in record_set]
    )
    if not df.empty:                      # Protect from KeyError if the dB is empty
        df.set_index('id', inplace=True)  # inplace = True saves us from having to bind a new dataframe
        # data.rename_axis(None)          # remove id label <- not working
        df.name = 'test'
        del df.index.name                 # remove id label
        # print(df)
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
