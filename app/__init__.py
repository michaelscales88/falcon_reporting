# """
# Boiler plate code from another project
# provides pagination for my sqlite mapped objects
# """
from __future__ import unicode_literals
from flask import Flask, render_template, g
from datetime import datetime


from app.src.factory import internal_connection
from app.models.flexible_storage import FlexibleStorage

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
# app.debug = config.DEBUG
# app.secret_key = config.SECRET_KEY

"""
Remove after for testing.
"""
app.connection = 'postgres://Chronicall:ChR0n1c@ll1337@10.1.3.17:9086/chronicall'
app.test_date = datetime.today().replace(year=2017, month=5, day=1, hour=0, minute=0, second=0)
app.statement = '''
    Select Distinct c_call.call_id, c_call.dialed_party_number, c_call.calling_party_number, c_event.*
    From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
    where
        to_char(c_call.start_time, 'YYYY-MM-DD') = '{date}' and
        c_call.call_direction = 1
    Order by c_call.call_id, c_event.event_id
    '''.format(date=str(app.test_date.date()))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.before_request
def before_request():
    # Set up our dB connection for pagination
    g.session = internal_connection(app.config['SQLALCHEMY_DATABASE_URI'], echo=True, cls=FlexibleStorage)


@app.teardown_request
def teardown(error):
    # Close out whatever for the app to exit
    g.session.close()

from app.views import index
from app.views import records
from app.views import insert

app.register_blueprint(index.mod)
app.register_blueprint(records.mod)
app.register_blueprint(insert.mod)
