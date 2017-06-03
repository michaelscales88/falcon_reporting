from flask import render_template, g, Blueprint, current_app, request, jsonify
from pandas import DataFrame
from sqlalchemy import func
import flask_excel as excel


from app.models.custom_model import model_factory
from app.models.flexible_storage import FlexibleStorage
from app.src.factory import internal_connection
from app.lib.sla_report import report

mod = Blueprint('build_report', __name__, template_folder='templates')
