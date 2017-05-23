from flask import render_template, g, Blueprint, current_app
from sqlalchemy import func

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
    print(test_report)
    return render_template(
        'report_viewer.html'
    )
