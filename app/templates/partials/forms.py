from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length

from app.models.user import User

from wtforms import SelectField, TextAreaField, StringField, validators, SelectMultipleField, FieldList, FormField


class BaseForm(FlaskForm):
    def __iter__(self):
        field_order = getattr(self, 'field_order', None)
        if field_order:
            temp_fields = []
            for name in field_order:
                if name == '*':
                    temp_fields.extend([f for f in self._unbound_fields if f[0] not in field_order])
                else:
                    temp_fields.append([f for f in self._unbound_fields if f[0] == name][0])
            self._unbound_fields = temp_fields
        return super(BaseForm, self).__iter__()


class SimpleForm(FlaskForm):
    # example = RadioField('Label', choices=[('value', 'description'), ('value_two', 'whatever')])
    example2 = SelectMultipleField(
        'Label2',
        choices=[('value', 'description'), ('value_two', 'whatever')],
        # coerce='utf-8',
        option_widget=None
    )


class MyForm(FlaskForm):
    name = StringField(u'Full Name', [validators.required(), validators.length(max=10)])
    address = TextAreaField(u'Mailing Address', [validators.optional(), validators.length(max=200)])


class ColumnEntryForm(FlaskForm):
    column = StringField()


class FrameColumns(BaseForm):
    columns = FieldList(FormField(ColumnEntryForm), min_entries=1)
    # field_order = ('username', '*')


def form_generator(columns):
    for column in columns:
        print(column)


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
