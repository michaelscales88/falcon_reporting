from flask import render_template, request, Blueprint

from app.core import redire


mod = Blueprint('builder', __name__, template_folder='templates')


@mod.route('/builder', methods=['POST', 'GET'])
def builder(back=None):

    return render_template('index.html')
