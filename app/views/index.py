from app import app
from pandas import read_sql
import flask_excel as excel
from flask import render_template, g, Blueprint, url_for, redirect
from flask_login import login_required

from app.core import query_model, insert_records, get_connection
from app.src.pandas_page import PandasPage
from app.src.save_widget import SaveWidget

mod = Blueprint('index', __name__, template_folder='templates')


# spruce up the css
# http://flask-appbuilder.readthedocs.io/en/latest/templates.html
@mod.route('/')
@mod.route('/index?=<int:page>', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):

    # need to check for records in db and get records if not present
    query, offset, total = query_model('sla_report', g.report_date, page, app.config['POSTS_PER_PAGE'])

    if not query or total == 0:
        records = get_connection(g.report_date)
        insert_records(g.session, 'sla_report', records)
        return redirect(url_for('index.index', page=1))

    df = read_sql(query.statement, query.session.bind)
    df.set_index(['call_id', 'event_id'], inplace=True)
    df.name = 'sla_report'
    pf = PandasPage(df, page, app.config['POSTS_PER_PAGE'], total)
    sw = SaveWidget(df.to_dict(orient='records'))
    sw.save()
    print('saved quote unquote')
    return redirect(url_for('save', data_set=df.to_dict(orient='records')))
    print('save 2')
    # print(sw.data)
    # for record in df.to_dict(orient='records'):
    #     print(record, type(record))
    # print(excel.make_response_from_tables(g.session, [Category, Post], "xls"))

    # print(excel.make_response_from_query_sets(df.to_records))
    # frame = DataFrame(records)
    # print(frame)
    # form = PostForm()
    # if form.validate_on_submit():
    #     post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user)
    #     db.session.add(post)
    #     db.session.commit()
    #     flash('Your post is now live!')
    #     return redirect(url_for('index'))
    # posts = g.user.followed_posts().paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('index.html',
                           title='Home',
                           report_date=g.report_date,
                           tables=[pf],
                           titles=[pf.frame.name],
                           save_widget=sw
                           )
