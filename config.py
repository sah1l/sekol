import os

#application directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'sekol',
        'user': 'sekol',
        'password': 'andnotbut',
    }

    # class Config(object):
    SQLALCHEMY_DATABASE_URI = "mysql://%(user)s:%(password)s@%(host)s/%(database)s" % DB_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable protection agains *Cross-site Request Forgery (Con e   SRF)*
    CSRF_ENABLED = True

    #secret key for signing the data. 
    CSRF_SESSION_KEY = "secret"

    # Secret key for signing cookies
    SECRET_KEY = "secret"

    UPLOAD_FOLDER = '/home/sahil/deep/website/data'