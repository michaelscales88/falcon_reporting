from app import app
from flask import flash, url_for, redirect
from app.src.factory import get_page_args, get_pagination, internal_connection
from flask_wtf import Form

from app.templates.partials.forms import SimpleForm
from app.templates.partials.forms import FrameColumns
from pandas import DataFrame, read_sql
from json import dumps
from flask import render_template, g, Blueprint, current_app, request
from flask_login import login_required
from datetime import datetime, timedelta
from app.core import query_model, insert_records, get_connection

mod = Blueprint('index', __name__, template_folder='templates')


@mod.route('/')
@mod.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    report_date = datetime.today().date()
    # need to check for records in db and get records if not present
    query, offset, total = query_model('sla_report', report_date, page, app.config['POSTS_PER_PAGE'])

    if not query or total == 0:
        records = get_connection(report_date)
        insert_records(g.session, 'sla_report', records)
        flash(
            'Added {number} records to {model_name}'.format(
                number=len(records),
                model_name='sla_report'
            )
        )
        return redirect(url_for('index.index'))
    # query, offset, total = query_model('sla_report', report_date, page, app.config['POSTS_PER_PAGE'])
    print(query.statement)
    df = read_sql(query.statement, query.session.bind)
    df.set_index(['call_id', 'event_id'], inplace=True)
    df.name = 'sla_report'
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
                           report_date=report_date,
                           tables=[df.to_html()],
                           titles=[df.name],
                           offset=offset,
                           total=total
                           )
# @mod.before_request
# def before_request():
#     # Set up our dB connection
#     model = current_app.data_src.model('sla_report')
#     if model:
#         g.db = internal_connection(
#             current_app.config['SQLALCHEMY_DATABASE_URI'],
#             echo=current_app.config['SQLALCHEMY_ECHO'],
#             cls=model
#         )
#
#
# # https://realpython.com/blog/python/primer-on-jinja-templating/
# @app.route('/index')
# @mod.route('/index', methods=["GET", "POST"])
# def records():
#     page, per_page, offset = get_page_args()
#     total_records = current_app.data_src.record_count('sla_report')
#     frame = current_app.data_src.page_view('sla_report', offset=offset, per_page=per_page)
#     frame.name = 'default'
#     try:
#         frame.set_index(['call_id', 'event_id'], inplace=True)  # inplace = True saves us from having to bind a new dataframe
#     except KeyError:
#         pass
#     pagination = get_pagination(
#         page=page,
#         per_page=per_page,
#         total=total_records,
#         record_name='id',
#         format_total=True,
#         format_number=True,
#     )
#     return render_template(
#         'index.html',
#         page=page,
#         per_page=per_page,
#         pagination=pagination,
#         tables=[fr.to_html(classes='report') for fr in (frame,) if not fr.empty],
#         titles=['na', tuple(fr.name for fr in (frame,) if not fr.empty)]
#     )
