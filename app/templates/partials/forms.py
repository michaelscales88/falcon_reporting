from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import BooleanField, StringField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class FrameForm(FlaskForm):
    mode = SelectField('Set Mode', default='Index', choices=[('Index', 'Index'), ('Pivot', 'Pivot')])
    index = SelectField('Set Index', choices=[])
    group = SelectField('Set group', choices=[])


class QueryForm(FlaskForm):
    model = SelectField('Model List', choices=[])
    start = DateField(
        'Start', format='%Y-%m-%d',
        default=datetime.today,
        validators=[DataRequired()]
    )
    end = DateField(
        'End', format='%Y-%m-%d',
        default=datetime.today,
        validators=[DataRequired()]
    )


class SaveForm(FlaskForm):
    file_name = StringField('file_name')

