from click import command, option
from flask import Flask, render_template


from app.src.factory import (
data_src, internal_connection, query_statement
)

app = Flask(__name__)
# app.config.from_pyfile('app.cfg')


@app.before_request
def before_request():
    # Set up our dB connections
    pass


@app.teardown_request
def teardown(error):
    # Close out whatever for the app to exit
    pass


@app.route('/')
def index():
    return """
    <h1>SLA REPORT</h1>
    """


@command()
@option('--port', '-p', default=5000, help='listening port')
def run(port):
    app.run(host='0.0.0.0', debug=True, port=port)

if __name__ == '__main__':
    run()
