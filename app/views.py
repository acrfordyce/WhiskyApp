from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.oauth import OAuthSignIn
from app import app, db, lm
from config import REVIEWS_PER_PAGE
from app.models import User, Whisky, Review
from app.forms import EditProfileForm, AddReviewForm, AddWhiskyForm, REGION_CHOICES
from datetime import datetime


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def before_request():
    if current_user.is_authenticated():
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
        db.session.commit()


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    user = current_user
    reviews = Review.query.order_by(Review.timestamp.desc()).paginate(page, REVIEWS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           user=user,
                           reviews=reviews)


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous():
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email, picture_uri = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        check_nickname = User.query.filter_by(nickname=username).first()
        if check_nickname:
            username = user.make_unique_nickname(nickname=username)
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    user.picture_uri = picture_uri
    db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    reviews = Review.query.filter_by(author=user).order_by(Review.timestamp.desc()).paginate(
        page, REVIEWS_PER_PAGE, False
    )
    return render_template('user.html',
                           title=user.nickname + ' profile',
                           user=user,
                           reviews=reviews)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditProfileForm(current_user.nickname)
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.about = form.about.data
        db.session.add(current_user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = current_user.nickname
        form.about.data = current_user.about
    return render_template('edit.html',
                           form=form,
                           title='Edit Profile')


@app.route('/add_review', methods=['GET', 'POST'])
@login_required
def add_review():
    form = AddReviewForm(current_user.nickname)
    whiskies = Whisky.query.order_by(Whisky.name.asc())
    choices = list(enumerate([whisky.name for whisky in whiskies], start=1))
    choices.insert(0, (0, 'Select a whisky'))
    form.whisky.choices = choices
    if form.validate_on_submit():
        whisky_display = dict(choices).get(form.whisky.data)
        whisky = Whisky.query.filter_by(name=whisky_display).first()
        review = Review(whisky=whisky, notes=form.notes.data, score=form.score.data, timestamp=datetime.utcnow(), author=current_user)
        db.session.add(review)
        db.session.commit()
        flash('Your review has been added.')
        return redirect(url_for('user', nickname=current_user.nickname))
    return render_template('add_review.html',
                           form=form,
                           title='Add Review')


@app.route('/edit_review/<review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    current_review = Review.query.filter_by(id=review_id).first()
    form = AddReviewForm(current_user.nickname)
    whiskies = Whisky.query.order_by(Whisky.name.asc())
    current_whisky_num = whiskies.all().index(current_review.whisky) + 1
    choices = list(enumerate([whisky.name for whisky in whiskies], start=1))
    form.whisky.choices = choices
    if form.validate_on_submit():
        if request.form['action'] == 'Cancel':
            print('Cancel Button')
            return redirect(url_for('user', nickname=current_user.nickname))
        print('Submit Button')
        whisky_display = dict(choices).get(form.whisky.data)
        whisky = Whisky.query.filter_by(name=whisky_display).first()
        current_review.whisky = whisky
        current_review.notes = form.notes.data
        current_review.score = form.score.data
        db.session.commit()
        flash('Your edits have been saved.')
        return redirect(url_for('user', nickname=current_user.nickname))
    else:
        form.whisky.data = current_whisky_num
        form.notes.data = current_review.notes
        form.score.data = current_review.score
    return render_template('edit_review.html',
                           form=form,
                           title='Edit Review'
    )


@app.route('/add_whisky', methods=['GET', 'POST'])
@login_required
def add_whisky():
    form = AddWhiskyForm()
    if form.validate_on_submit():
        region_display = dict(REGION_CHOICES).get(form.region.data)
        whisky = Whisky(name=form.name.data, age_statement=form.age_statement.data, region=region_display)
        db.session.add(whisky)
        db.session.commit()
        flash('Added whisky to database.')
        return redirect(url_for('add_review', nickname=current_user.nickname))
    return render_template('add_whisky.html',
                           form=form,
                           title='Submit Whisky')


@app.route('/whisky/<name>')
@app.route('/whisky/<name>/<int:page>')
@login_required
def whisky(name, page=1):
    whisky = Whisky.query.filter_by(name=name).first()
    if whisky is None:
        flash('Entry for {0} not found.'.format(name))
        return redirect(url_for('index'))
    reviews = Review.query.filter_by(whisky=whisky).order_by(Review.timestamp.desc()).paginate(
        page, REVIEWS_PER_PAGE, False
    )
    return render_template('whisky.html',
                           whisky=whisky,
                           reviews=reviews,
                           title=whisky.name)


@app.route('/whisky_list')
@login_required
def whisky_list():
    whiskies = Whisky.query.all()
    return render_template('whisky_list.html',
                           whiskies=whiskies,
                           title='Whisky List'
    )


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404