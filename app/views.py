from flask import render_template, flash, redirect, session, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, oid
from app.models import User, Whisky, Review
from app.forms import LoginForm, EditProfileForm, AddReviewForm, AddWhiskyForm, REGION_CHOICES
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
def index():
    user = current_user
    return render_template('index.html',
                           title='Home',
                           user=user)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User {0} not found.'.format(nickname))
        return redirect(url_for('index'))
    reviews = Review.query.filter_by(author=current_user).order_by(Review.timestamp.desc()).all()
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


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404