from flask import render_template, url_for, flash, redirect, request
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm
from application.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    return render_template("hello.html")

@app.route("/about")
def about():
    return render_template("goodbye.html", title = 'About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #hash the value of the password and add new User class's instance 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        #add the newly created user instance to the db
        db.session.add(user)
        db.session.commit()
        flash('Account created for {}'.format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template("register.html", title = 'Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_request = request.args.get('next')
            return redirect(next_request) if next_request else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check the username or password.", "danger")
    return render_template("login.html", title = 'Login', form=form) 



@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title='Account')