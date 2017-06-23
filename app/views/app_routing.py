from flask import render_template, flash, redirect, url_for, request, g, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, lm, si
from urllib.parse import urlparse, urljoin
from datetime import datetime


from app.models.user import User
from app.templates.partials.forms import LoginForm, SearchForm
from app.core import get_count


@app.before_request
def before_request():
    print('setup')
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.session = db.session
        g.model_registry = app.model_registry
        g.report_date = datetime.today().date()
        if app.config['ENABLE_SEARCH']:
            si.register_class(User)  # update whoosh with User information
            # for model in g.model_registry:
            #     if model:
            #         si.register_class(model)    # update whoosh with custom models
            g.search_form = SearchForm()


@app.teardown_request
def teardown(error):
    print('teardown')
    session = getattr(g, 'session', None)
    if app.debug and app.config['WIPE_SESSION']:
        registry = getattr(g, 'model_registry', None)
        if registry:
            model = registry['sla_report']
            if model and get_count(model.query) > app.config['MAX_RECORDS']:
                mm = model.query.all()
                for m in mm:
                    session.delete(m)
                session.commit()

    if session:
        session.remove()     # Close scoped session


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user_email = str(form.login.data)
        user = User.query.filter_by(email=user_email).first()
        # remember_me = False
        # if 'remember_me' in session:
        #     remember_me = session['remember_me']
        #     session.pop('remember_me', None)
        # login_user(user, remember=remember_me)
        if not user:
            nickname = user_email.split('@')[0]
            nickname = User.make_unique_nickname(nickname)
            user = User(nickname=nickname, email=user_email)
            db.session.add(user)
            db.session.commit()
            # make the user follow him/herself
            # db.session.add(user.follow(user))
            # db.session.commit()

        login_user(user)
        flash('Logged in successfully.')

        next = request.args.get('next')
        if not is_safe_url(next):
            return abort(400)

        return redirect(next or url_for('index.index'))
    return render_template('login.html',
                           title='Sign In',
                           form=form)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https')
        and ref_url.netloc == test_url.netloc
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))


@lm.user_loader
def load_user(id):
    return User.get(id=int(id))


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index.index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))


@app.route('/search_results/<query>')
@login_required
def search_results(query):
    model_name = 'sla_report'
    model = g.model_registry[model_name]

    if not model:
        redirect(url_for('index.index'))

    results = User.search_query(query)
    print(results, dir(results))
    return render_template('search_results.html',
                           query=query,
                           results=results)
