from flask import render_template, g, Blueprint, url_for, redirect
from flask_login import login_required
from pandas import read_sql

from app import app
from app.core import get_count
from app.src.pandas_page import PandasPage
from app.user.models import User

# from app.src.save_widget import SaveWidget


mod = Blueprint('search', __name__, template_folder='templates')


@mod.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index.index'))
    return redirect(url_for('search.search_results', query=g.search_form.search.data))


@mod.route('/search_results/<query>')
@mod.route('/search_results/<query>/<int:page>', methods=['GET', 'POST'])
@login_required
def search_results(query, page=1):
    model_name = 'sla_report'
    model = g.model_registry[model_name]

    # need to check for records in db and get records if not present
    # query, offset, total = query_model('sla_report', g.report_date, page, app.config['POSTS_PER_PAGE'])

    if not model:
        redirect(url_for('index.index'))

    user_results = User.search_query(query)
    model_results = model.search_query(query)
    df = read_sql(model_results.statement, model_results.session.bind)
    df.set_index(['call_id', 'event_id'], inplace=True)
    df.name = 'sla_report'
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], get_count(model_results))
    # print(type(model_results), model_results.statement)
    return render_template('search_results.html',
                           query=query,
                           user_results=user_results,
                           tables=[pf],
                           titles=[pf.frame.name]
                           )