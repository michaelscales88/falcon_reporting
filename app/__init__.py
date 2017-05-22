from flask import Flask, redirect

from .ext.database import SQLAlchemy
from .db_models.base import Model


PER_PAGE = 20

app = Flask(__name__)
db = SQLAlchemy(app, Model=Model)


@app.route('/')
def homepage():
    text = """
    <h1>SLA REPORT</h1>
    """
    return text

#
# @app.route('/users/', defaults={'page': 1})
# @app.route('/users/page/<int:page>')
# def show_users(page):
#     count = count_all_users()
#     users = get_users_for_page(page, PER_PAGE, count)
#     if not users and page != 1:
#         abort(404)
#     pagination = Pagination(page, PER_PAGE, count)
#     return render_template('users.html',
#         pagination=pagination,
#         users=users
#     )
#
#
# def url_for_other_page(page):
#     args = request.view_args.copy()
#     args['page'] = page
#     return url_for(request.endpoint, **args)
# app.jinja_env.globals['url_for_other_page'] = url_for_other_page