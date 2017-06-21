from app import app
from app.src.factory import get_page_args, get_pagination, internal_connection
from flask_wtf import Form

from app.templates.partials.forms import SimpleForm
from app.templates.partials.forms import FrameColumns
from flask import render_template, g, Blueprint, current_app, request

mod = Blueprint('index', __name__, template_folder='templates')


@mod.route('/')
# @app.route('/index', methods=['GET', 'POST'])
# @app.route('/index/<int:page>', methods=['GET', 'POST'])
# @login_required
def index(page=1):
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
                           # form=form,
                           # posts=posts
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
