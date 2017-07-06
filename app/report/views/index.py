from flask import render_template, g, Blueprint, url_for, redirect, request
from flask_login import login_required

from app import app
from app.core import query_model, insert_records, get_connection, save, get_count, get_frame
from app.report.src.pandas_page import PandasPage
from app.templates import QueryForm, SaveForm

mod = Blueprint('index', __name__, template_folder='templates')


# spruce up the css
# http://flask-appbuilder.readthedocs.io/en/latest/templates.html
@mod.route('/')
@mod.route('/index?=<int:page>', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    # need to check for records in db and get records if not present
    query_form = QueryForm()
    save_form = SaveForm()

    # if request.method == 'GET':
    query = query_model(app.config['DEFAULT_MODEL'], g.report_date, page, app.config['POSTS_PER_PAGE'])
    # print('GET', app.config['DEFAULT_MODEL'], query)

    if not query:
        print(not query)
        print('added records. query:', query)
        records = get_connection(g.report_date)
        insert_records(g.session, 'sla_report', records)
        # return redirect(url_for('builder.records', back='index.index'))
        return redirect(url_for('index.index', page=1))

    # Get a DataFrame instance of the query
    # If query is None df is an empty frame
    df = get_frame(query, name='sla_report')

    # Count the total number of records in the query
    # If query is None total is 0
    total = get_count(query)

    if request.method == 'POST':
        form_name = request.form.get('form-name')
        if form_name == 'save' and save_form.validate_on_submit():
            return save(df, file_name=str(save_form.file_name.data))

        # TODO I want to put this into builder or the custom record view
        # if form_name == 'display' and query_form.validate_on_submit():
        #     print('inside query_form validate')
        #     query, offset, total = query_model(query_form.model.data, g.report_date, page, app.config['POSTS_PER_PAGE'])

    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template('index.html',
                           title='Home',
                           report_date=g.report_date,
                           table=pf,
                           tablename=pf.frame.name,
                           query_form=query_form,
                           save_form=save_form
                           )
