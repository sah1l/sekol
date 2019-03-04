from flask import url_for, redirect, render_template

from app import app


@app.route('/')
def index():
    return redirect(url_for("home"))

@app.route('/home')
def home():
    return render_template('pages/placeholder.home.html')

@app.route('/services')
def services():
    return render_template('pages/placeholder.services.html')

@app.route('/contact')
def contact():
    return render_template('pages/placeholder.contact.html')


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404
