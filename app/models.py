from app import db


class Whisky(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    age_statement = db.Column(db.String(5))
    region = db.Column(db.String(120))
    abv = db.Column(db.Float)
    reviews = db.relationship('Review', backref='whisky', lazy='dynamic')

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    reviews = db.relationship('Review', backref='author', lazy='dynamic')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whisky_id = db.Column(db.Integer, db.ForeignKey('whisky.id'))
    body = db.Column(db.String(500))
    timestamp= db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
