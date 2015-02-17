from app import db
from flask_login import UserMixin


class Whisky(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    age_statement = db.Column(db.String(3))
    region = db.Column(db.String(120))
    reviews = db.relationship('Review', backref='whisky', lazy='dynamic')

class User(UserMixin,   db.Model):
    id = db.Column(db.Integer, primary_key=True)
    social_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(64), index=True)
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
    picture_uri = db.Column(db.String(140))
    reviews = db.relationship('Review', backref='author', lazy='dynamic')
    last_seen = db.Column(db.DateTime)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        new_nickname = ''
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def avatar(self, social_id, size):
        user = User.query.filter_by(social_id=social_id).first()
        if user.social_id.split('$')[0] == 'facebook':
            facebook_id = user.social_id.split('$')[1]
            return 'http://graph.facebook.com/{0}/picture/?type={1}'.format(facebook_id, size)
        elif user.social_id.split('$')[0] == 'twitter':
            return user.picture_uri
        elif user.social_id.split('$')[0] == 'google':
            if size == 'small':
                return user.picture_uri + '?sz=50'
            return user.picture_uri + '?sz=250'


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whisky_id = db.Column(db.Integer, db.ForeignKey('whisky.id'))
    notes = db.Column(db.String(500))
    score = db.Column(db.Integer)
    timestamp= db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
