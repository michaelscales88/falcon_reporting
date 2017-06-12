from flask_wtf import Form
from wtforms import RadioField


class SimpleForm(Form):
    example = RadioField('Label', choices=[('value', 'description'), ('value_two', 'whatever')])
