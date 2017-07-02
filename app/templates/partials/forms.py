from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length

from app.models.user import User

from wtforms import SelectField, TextAreaField, StringField, validators, SelectMultipleField, FieldList, FormField


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])


class QueryForm(FlaskForm):
    model = StringField('model',  validators=[DataRequired()])


class SaveForm(FlaskForm):
    save_directory = StringField('save_dir')

