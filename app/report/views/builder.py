from flask import render_template, request, Blueprint

from app.core import redirect_back


mod = Blueprint('builder', __name__, template_folder='templates')


@mod.route('/builder', methods=['POST', 'GET'])
def records(model_name, start=None, end=None, back=None):
    # Builder handles making queries.
    # If records are not present it retrieves them from their source

    if back:
        redirect_back(back)
    return render_template('index.html')
