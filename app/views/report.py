import flask_excel as excel
from flask import render_template, Blueprint, g, redirect, url_for
from pandas import DataFrame
from flask_login import login_required

from app import app
from app.src.sla_cache import cache
from app.src.pandas_page import PandasPage
from app.core import query_model


from app.src.sla_report import sla_report


mod = Blueprint('report', __name__, template_folder='templates')


@mod.route('/')
@mod.route('/report', methods=['GET', 'POST'])
@mod.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def report(page=1):
    query, offset, total = query_model('sla_report', g.report_date, 0, 0)

    if not query:
        return redirect(url_for('index.index'))

    cached_list = cache(query.all(), pk='call_id', subkey='event_id')
    test_report = sla_report(
        cached_list, 
        client_list=list(app.config['CLIENTS'])  # if app.config.get('CLIENTS', None) else ['Torie', 'Sean', 'Susan', 'Debbie']
    )
    
    test_report.name = str(g.report_date)
    test_report_content = test_report.to_dict()
    # TODO 3: This should likely be its own 'pyexcel' model or something of the like
    df = DataFrame.from_items(
        [col for col in test_report_content.items()]
    )
    df.name = 'sla_report'
    df.index = [''] + list(app.config['CLIENTS'])  # if app.config.get('CLIENTS', None) else ['Torie', 'Sean', 'Susan', 'Debbie'])
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template(
        'report.html',
        tables=[pf],
        titles=[pf.frame.name]
    )

