from flask import render_template, g, Blueprint, url_for, redirect, request
from flask_login import login_required
from pandas import pivot_table

from app import app
from app.core import query_model, insert_records, get_connection, save, get_count, get_frame
from app.src.pandas_page import PandasPage
from app.templates.partials.forms import QueryForm, SaveForm, FrameForm

mod = Blueprint('index', __name__, template_folder='templates')


# spruce up the css
# http://flask-appbuilder.readthedocs.io/en/latest/templates.html
@mod.route('/')
@mod.route('/index?=<int:page>', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    # need to check for records in db and get records if not present
    frame_form = FrameForm()
    query_form = QueryForm()
    save_form = SaveForm()
    print('form choice:', query_form.model.data)
    model_name = query_form.model.data
    print(g.model_registry[model_name])
    # if request.method == 'GET':
    query = query_model(
        app.config['DEFAULT_MODEL'] if query_form.model.data == 'None' else query_form.model.data,
        query_form.start.data,
        page,
        app.config['POSTS_PER_PAGE']
    )
    # print('GET', app.config['DEFAULT_MODEL'], query)

    if not query:
        print(not query)
        print('added records. query:', query)
        records = get_connection(query_form.start.data)
        insert_records(g.session, app.config['DEFAULT_MODEL'], records)
        # return redirect(url_for('builder.records', back='index.index'))
        return redirect(url_for('index.index', page=1))

    # Count the total number of records in the query
    # If query is None total is 0
    total = get_count(query)
    print('updated total', total, query)
    # Get a DataFrame instance of the query
    # If query is None df is an empty frame
    query = query.limit(app.config['POSTS_PER_PAGE'])

    offset = (page - 1) * app.config['POSTS_PER_PAGE']

    if offset > 0:  # only need to offset if we need more than one page?
        print('offsetting', offset)
        query = query.offset(offset)

    # df = get_frame(query, name='sla_report')
    df = query.frame()
    df.name = app.config['DEFAULT_MODEL']
    # print(df)
    # print(query.frame())
    # print(query.statement)
    if frame_form.is_submitted():
        form_name = request.form.get('form-name')
        if form_name == 'frame' and frame_form.mode.data == 'Index':
            df.set_index([frame_form.index.data, frame_form.group.data], inplace=True)
        elif form_name == 'frame' and frame_form.mode.data == 'Pivot':
            df.unstack()
            # df = df.pivot(index=str(frame_form.index.data), columns=frame_form.group.data)['event_id']
            df = pivot_table(df, index=frame_form.index.data, columns=frame_form.group.data)
            df.name = app.config['DEFAULT_MODEL']
        else:
            pass

    if request.method == 'POST':
        form_name = request.form.get('form-name')
        if form_name == 'save' and save_form.validate_on_submit():
            return save(df, file_name=str(save_form.file_name.data))

            # TODO I want to put this into builder or the custom record view
            # if form_name == 'display' and query_form.validate_on_submit():
            #     print('inside query_form validate')
            #     query, offset, total = query_model(query_form.model.data, g.report_date, page, app.config['POSTS_PER_PAGE'])

    query_form.model.choices = [(c.__name__, c.__name__) for c in g.model_registry]
    query_form.model.data = (query_form.model.id
                             if query_form.model
                             else app.config['DEFAULT_MODEL'])
    frame_form.index.choices = [(l, l) for l in list(df)]
    frame_form.group.choices = frame_form.index.choices
    print('i think my total is', total)
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    return render_template('index.html',
                           title='Home',
                           report_date=g.report_date,
                           table=pf,
                           tablename=pf.frame.name,
                           query_form=query_form,
                           save_form=save_form,
                           frame_form=frame_form
                           )
