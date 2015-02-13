from app import db
from hashlib import md5


class Whisky(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    age_statement = db.Column(db.String(5))
    region = db.Column(db.String(120))
    abv = db.Column(db.Float)
    reviews = db.relationship('Review', backref='whisky', lazy='dynamic')
    about = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    about = db.Column(db.String(140))
    email = db.Column(db.String(120), index=True, unique=True)
    reviews = db.relationship('Review', backref='author', lazy='dynamic')

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
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whisky_id = db.Column(db.Integer, db.ForeignKey('whisky.id'))
    notes = db.Column(db.String(500))
    score = db.Column(db.Integer)
    timestamp= db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
