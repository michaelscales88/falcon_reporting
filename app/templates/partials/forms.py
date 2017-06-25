from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired, Length

from app.models.user import User

from wtforms import SelectField, TextAreaField, StringField, validators, SelectMultipleField, FieldList, FormField


# class BaseForm(FlaskForm):
#     def __iter__(self):
#         field_order = getattr(self, 'field_order', None)
#         if field_order:
#             temp_fields = []
#             for name in field_order:
#                 if name == '*':
#                     temp_fields.extend([f for f in self._unbound_fields if f[0] not in field_order])
#                 else:
#                     temp_fields.append([f for f in self._unbound_fields if f[0] == name][0])
#             self._unbound_fields = temp_fields
#         return super(BaseForm, self).__iter__()


class LoginForm(FlaskForm):
    login = StringField('login', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])

