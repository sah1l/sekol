from flask import Blueprint, redirect, url_for, flash, render_template
from flask_login import current_user, login_user, logout_user

from app.models import User
from app.mod_auth.forms import LoginForm


# define Blueprint for auth module
mod_auth = Blueprint('auth', __name__, url_prefix='/login')

@mod_auth.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        user = User.query.filter_by(name=current_user.name).first()
        if user:
            return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data
        passw = form.password.data
        try:
            data = User.query.filter_by(name=name, password=passw).first()
            print data
            if data is not None:
                login_user(data, remember=form.remember_me.data)
                return redirect(url_for('home'))
            else:
                flash('enter valid user and password')
                return redirect(url_for('auth.login'))
        except Exception as ex:
                print str(ex)
                flash('something went wrong')
                return redirect(url_for('auth.login'))

    return render_template('forms/login.html', form=form)


@mod_auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))