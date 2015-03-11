import os


basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') + '?check_same_thread=False'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

WTF_CSRF_ENABLED = True
SECRET_KEY = 'I-love-Scotch'

OAUTH_PROVIDERS = {
    'facebook': {
        'id': '700744030042277',
        'secret': '9535c8cc76e26fcd510c15c780cc1b57'
    },
    'twitter': {
        'id': 'rjM5DadWK0zWgRjIZN9LAcX5r',
        'secret': 'rS8GCDmeHCygWBWCOuNBlH83Qof0fAAk7TItKGqM5JBc9q6Ygs',
        'access_token': '422224182-QPE9OYk9IvoDHmo833S4pvY7O3fRFWtzdbeiVog0',
        'access_secret': 't30eB35U2xxNBYH3VoBOJjC8wGTzfrUeK9EfriPUwjvH0'
    },
    'google': {
        'id': '77305032384-kfc4anuckhqvlirvprffberm7e5cmh7s.apps.googleusercontent.com',
        'secret': 'H13dFDZCleSmU9k_-yCUrrP_'
    }
}

REVIEWS_PER_PAGE = 5