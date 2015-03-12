from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .momentjs import Momentjs


app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.globals['momentjs'] = Momentjs
db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/WhiskyApp.log', 'a', 1*1024*1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('WhiskyApp startup')


from app import views, models