import os


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'I-love-Scotch'

OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'http://www.google.com/profiles/<username>'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
]

OAUTH_PROVIDERS = {
    'facebook': {
        'id': '700744030042277',
        'secret': '9535c8cc76e26fcd510c15c780cc1b57'
    }
}