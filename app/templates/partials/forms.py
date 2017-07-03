from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class QueryForm(FlaskForm):
    model = StringField('model',  validators=[DataRequired()])
    # this will need js in order to make it a datetime picker
    start = DateField('Start', format="%m/%d/%Y",  validators=[DataRequired()])
    end = DateField('End', format="%m/%d/%Y",  validators=[DataRequired()])


class SaveForm(FlaskForm):
    save_directory = StringField('save_dir')

