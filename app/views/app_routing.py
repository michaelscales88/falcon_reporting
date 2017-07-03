from flask import render_template, flash, redirect, url_for, request, g
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

from app import app, db, lm, si
from app.models import User
from app.core import get_count, redirect_back, get_redirect_target
from app.templates.partials.forms import LoginForm, SearchForm


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
            if app.model_registry:
                for model in app.model_registry:
                    if model:
                        model.metadata.create_all(g.session.bind)  # Make schema and bind to engine
                        si.register_class(model)    # update whoosh to any changes to the schema model
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
                print('removed some records')
                flash('Removed {number} of records from {model_name}'.format(number=len(mm), model_name='sla_report'))
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
    next = get_redirect_target()
    form = LoginForm()

    if request.method == 'POST':

        if g.user is not None and g.user.is_authenticated:
            return redirect(url_for('index.index'))

        if form.validate_on_submit():
            user_email = str(form.login.data)
            user = User.query.filter_by(email=user_email).first()

            if not user:
                nickname = user_email.split('@')[0]
                nickname = User.make_unique_nickname(nickname)
                user = User(nickname=nickname, email=user_email)
                db.session.add(user)
                db.session.commit()

            # remember_me = False
            # if 'remember_me' in g.session:
            #     remember_me = g.session['remember_me']
            #     g.session.pop('remember_me', None)
            # login_user(user, remember=remember_me)
            login_user(user)
            flash('Logged in successfully.')
            return redirect_back('index.index')
    return render_template('login.html',
                           title='Sign In',
                           next=next,
                           form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index.index'))


@lm.user_loader
def load_user(id):
    return User.get(id=int(id))

