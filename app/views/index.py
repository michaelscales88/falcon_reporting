from app import app
from pandas import read_sql, DataFrame
from flask import render_template, g, Blueprint, url_for, redirect, request
from flask_login import login_required

from app.core import query_model, insert_records, get_connection, save, get_count
from app.src.pandas_page import PandasPage
from app.templates.partials.forms import QueryForm, SaveForm

mod = Blueprint('index', __name__, template_folder='templates')


# spruce up the css
# http://flask-appbuilder.readthedocs.io/en/latest/templates.html
@mod.route('/')
@mod.route('/index?=<int:page>', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    # need to check for records in db and get records if not present
    query = None
    query_form = QueryForm()
    save_form = SaveForm()

    if request.method == 'GET':
        query, offset, total = query_model(app.config['DEFAULT_MODEL'], g.report_date, page,
                                           app.config['POSTS_PER_PAGE'])
        print('GET', app.config['DEFAULT_MODEL'], query)

    if request.method == 'POST':
        form_name = request.form.get('form-name')
        print('found form_name', form_name)
        print('checking post forms')
        if form_name == 'save' and save_form.validate_on_submit():
            print('inside save')
        if form_name == 'display' and query_form.validate_on_submit():
            print('inside query_form validate')
            query, offset, total = query_model(query_form.model.data, g.report_date, page, app.config['POSTS_PER_PAGE'])

    if not query:
        print(not query)
        print('added records. query:', query)
        records = get_connection(g.report_date)
        insert_records(g.session, 'sla_report', records)
        return redirect(url_for('index.index', page=1))

    if query:
        df = read_sql(query.statement, query.session.bind)
        df.set_index(['call_id', 'event_id'], inplace=True)
        df.name = 'sla_report'
        total = get_count(query)
        print(total)
    else:
        df = DataFrame()
        df.name = 'empty'
        total = 0

    # print('save stuff')
    # print(request.method)
    # print(save_form.validate_on_submit())
    # if request.method == 'GET':
    #     print('checking get forms')
    #     if save_form.validate_on_submit():
    #         print('inside save')
    #         return save(df)
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template('index.html',
                           title='Home',
                           report_date=g.report_date,
                           table=pf,
                           tablename=pf.frame.name,
                           query_form=query_form,
                           save_form=save_form
                           )
