from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

from slugify import slugify
import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
app.secret_key = 'lasdkfjalsj234kjlkjvi234'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None

@app.before_request
def before_request():
    """Connect to the database before each request"""
    g.db = models.DATABASE
    g.db.get_conn()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request"""
    g.db.close()
    return response

@app.route('/')
def index():
    posts = models.Post.select().limit(100)
    return render_template('index.html', posts=posts)


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("Yay you registered!", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/new_post', methods=('GET', 'POST'))
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        models.Post.create(user=g.user.id,
                           title=form.title.data.strip(),
                           timespent=form.timespent.data.strip(),
                           learned=form.learned.data.strip(),
                           slug=slugify(form.title.data.strip()),
                           resources=form.resources.data.strip(),
                           )
        flash("Message posted! Thanks!", "success")
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries')
def entries():
    posts = models.Post.select().limit(100)
    return render_template('index.html', posts=posts)


@app.route('/entries/<slug>')
@app.route('/entries/edit/<slug>')
@app.route('/entries/delete/<slug>')
@app.route('/entry')


@app.route('/detail/<slug>')
def view_details(slug):
    posts = models.Post.select().where(models.Post.slug == slug)
    return render_template('detail.html', posts=posts)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='cdogstu99',
            email='crstuart@gmail.com',
            password='password',
            admin = True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)