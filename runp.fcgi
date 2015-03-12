#!bin/python

from config import SQLALCHEMY_DATABASE_URI
import os
os.environ['DATABASE_URL'] = SQLALCHEMY_DATABASE_URI


from flipflop import WSGIServer
from app import app


if __name__ == '__main__':
    WSGIServer(app).run()