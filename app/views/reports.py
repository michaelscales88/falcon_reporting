from flask import render_template, g, Blueprint, current_app
from sqlalchemy import func
import pandas as pd

from app.src.factory import get_page_args, get_pagination
from app.models.flexible_storage import FlexibleStorage
from app.tests.report_test import report

mod = Blueprint('reports', __name__, template_folder='templates')


# TODO this is ripe for flask-excel extension for upload/download
# TODO 2: Sheet.save_to_database(session, table[, ...])	Save data in sheet to database table
@mod.route('/run/')
@mod.route('/run')
def run_report():
    record_set = g.session.query(FlexibleStorage).order_by(FlexibleStorage.id).filter(func.date(current_app.test_date)).all()
    test_report = report(record_set)
    # TODO https://sarahleejane.github.io/learning/python/2015/08/09/simple-tables-in-webapps-using-flask-and-pandas-with-python.html
    # data = pd.read_excel(test_report)
    # data.set_index(['Name'], inplace=True)
    # data.index.name = None
    # females = data.loc[data.Gender == 'f']
    # males = data.loc[data.Gender == 'm']
    # return render_template('view.html', tables=[females.to_html(classes='female'), males.to_html(classes='male')],
    #                        titles=['na', 'Female surfers', 'Male surfers'])
    # print(test_report)
    return render_template(
        'report_viewer.html'
    )
