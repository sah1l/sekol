from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, SubmitField, SelectMultipleField, PasswordField, BooleanField, widgets, SelectField
from wtforms.validators import DataRequired, EqualTo, Length

from app.models import User, Category, Design
import re


class UserInfoForm(FlaskForm):
    """
    Edit user form

    Fields:

    - username (string field)
    - is_admin (checkbox)
    - organizations (select multiple field)
    """
    username = StringField('name', validators=[DataRequired()])
    type = SelectField(u'User type', choices=[('dealer', 'dealer'), ('designer', 'designer')])
    allow_create = BooleanField('Allowed to create users', default=False)
    allow_upload = BooleanField('Allowed to add categories', default=False)
    submit = SubmitField('Update')


class PasswordForm(FlaskForm):
    """
    Edit password form

    Fields:

    - type password (password field)
    - retype password (password field)
    """
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=20)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update password')


class UserCreateForm(UserInfoForm, PasswordForm):
    """
    Registration form for new user.

    Consists of UserInfoForm, EmailForm, PasswordForm and personal submit button.
    Custom validation.
    """
    submit = SubmitField('Add user')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Checks if user exists already (by email)

        :return: If the user exists already, return False, else True
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter_by(name=self.username).first()

        if user:
            self.username.errors.append("This username is already taken.")
            return False

        return True


class CategoryInfoForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired()])
    users = SelectMultipleField('Users',
                                widget=widgets.TableWidget(with_table_tag=True),
                                option_widget=widgets.CheckboxInput(),
                                coerce=str)
    submit = SubmitField('Save')


class CategoryCreateForm(CategoryInfoForm):
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.category = None

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        cat = Category.query.filter_by(name=self.name.data).first()
        if cat:
            self.name.errors.append("A category with this name exists already.")
            return False

        return True


class DesignInfoForm(FlaskForm):
    name = StringField('Design Name', validators=[DataRequired()])
    file = FileField('Design Image', validators=[FileRequired()])
    categories = SelectMultipleField('Categories',
                                widget=widgets.TableWidget(with_table_tag=True),
                                option_widget=widgets.CheckboxInput(),
                                coerce=str)
    submit = SubmitField('Save')

    def validate(self):
        return True

class DesignCreateForm(DesignInfoForm):
    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.design = None


    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        design = Design.query.filter_by(name=self.name.data).first()
        if design:
            self.name.errors.append("A design with this name exists already.")
            return False

        return True