from flask import render_template, Blueprint, g, redirect, url_for, request
from app.report.src.sla_report import sla_report
from flask import render_template, Blueprint, g, redirect, url_for
from flask_login import login_required
from pandas import DataFrame

from app import app
from app.src.pandas_page import PandasPage
from app.report.src.sla_cache import cache
from app.core import query_model, insert_records, get_connection, save, get_count, get_frame
from app.templates.partials.forms import QueryForm, SaveForm

mod = Blueprint('report', __name__, template_folder='templates')


@mod.route('/')
@mod.route('/report', methods=['GET', 'POST'])
@mod.route('/report/<int:page>', methods=['GET', 'POST'])
@login_required
def report(page=1):
    query_form = QueryForm()
    save_form = SaveForm()

    # if request.method == 'GET':
    query = query_model(app.config['DEFAULT_MODEL'], g.report_date, page, app.config['POSTS_PER_PAGE'])

    if not query:
        print(not query)
        print('added records. query:', query)
        records = get_connection(g.report_date)
        insert_records(g.session, 'sla_report', records)
        # return redirect(url_for('builder.records', back='index.index'))
        return redirect(url_for('index.index', page=1))

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

    # Count the total number of records in the query
    # If query is None total is 0
    total = get_count(query)

    if request.method == 'POST':
        form_name = request.form.get('form-name')
        if form_name == 'save' and save_form.validate_on_submit():
            return save(df, file_name=str(save_form.file_name.data))

    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template(
        'report.html',
        tables=[pf],
        titles=[pf.frame.name]
    )

