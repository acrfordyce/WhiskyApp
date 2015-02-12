from app import db


class Whisky(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    age_statement = db.Column(db.String(5))
    region = db.Column(db.String(120))
    abv = db.Column(db.Float)