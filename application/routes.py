from flask import render_template, url_for, flash, redirect
from application import app
from application.forms import RegistrationForm, LoginForm
from application.models import User, Post

@app.route("/")
@app.route("/home")
def home():
    return render_template("hello.html")

@app.route("/about")
def about():
    return render_template("goodbye.html", title = 'About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash('Account created for {}'.format(form.username.data), 'success')
        return redirect(url_for('home'))
    return render_template("register.html", title = 'Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'nkprod@apple.com' and form.password.data == '123456789':
            flash("You have successfully logged in", "success")
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check the username or password.", "danger")
    return render_template("login.html", title = 'Login', form=form) 