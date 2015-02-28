from flask_wtf import Form
from wtforms import StringField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length
from app.models import User, Whisky


REGION_CHOICES = [
        (1, "Blend"),
        (2, "Campbeltown"),
        (3, "Highland"),
        (4, "Island"),
        (5, "Islay"),
        (6, "Lowland"),
        (7, "Speyside")
    ]


class EditProfileForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    about = TextAreaField('about', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True


class AddReviewForm(Form):
    whisky = SelectField('whisky', choices=[], coerce=int, validators=[DataRequired()])
    notes = TextAreaField('notes')
    score = IntegerField('score', validators=[DataRequired()])

    def __init__(self, nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.author = nickname


class AddWhiskyForm(Form):
    name = StringField('name', validators=[DataRequired(), Length(min=1, max=120)])
    age_statement = StringField('age_statement', validators=[DataRequired(), Length(min=1, max=3)])
    region = SelectField('region', choices=REGION_CHOICES, coerce=int)

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)

    def validate(self):
        if not Form.validate(self):
            return False
        whisky = Whisky.query.filter_by(name=self.name.data).first()
        if whisky != None:
            self.name.errors.append('This whisky is already in the database.')
            return False
        return True