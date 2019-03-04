from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from app.models import User
from sqlalchemy import func

# Set your classes here.

class LoginForm(FlaskForm):
    name = TextField('name', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        """
        Checks user's email
        If email does not exist, show an error
        :return:
        """
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        user = User.query.filter(func.lower(User.name)==func.lower(self.name.data)).first()
        if not user:
            self.name.errors.append("This name is not registered. Contact Admin to add user.")
            return False

        return True