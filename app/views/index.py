from flask import render_template, g, Blueprint
from pandas import DataFrame


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
    print(type(record_set), record_set)
    # test_report = report(record_set)
    # test_report.name = 'Bitching Baby'
    # test_report_rownames = test_report.rownames
    # test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    data = DataFrame(record_set)
    # data = DataFrame.from_items(
    #     [col for col in record_set.items()]
    # )
    # data.index = test_report_rownames
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
        tables=[data.to_html(classes='report')],
        titles=['na', 'test']
    )
