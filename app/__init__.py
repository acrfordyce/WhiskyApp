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


from app import views, models