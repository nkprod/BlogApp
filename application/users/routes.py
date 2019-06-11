from flask import Blueprint,render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from application import db, bcrypt
from application.models import User, Post
from application.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, PasswordResetForm
from application.users.utils import save_picture, send_reset_email



users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        #hash the value of the password and add new User class's instance 
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        #add the newly created user instance to the db
        db.session.add(user)
        db.session.commit()
        flash('Account created for {}'.format(form.username.data), 'success')
        return redirect(url_for('users.login'))
    return render_template("register.html", title = 'Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_request = request.args.get('next')
            return redirect(next_request) if next_request else redirect(url_for('main.home'))
        else:
            flash("Login Unsuccessful. Please check the username or password.", "danger")
    return render_template("login.html", title = 'Login', form=form) 


# @app.route("/updateAccount", methods=['GET', 'POST'])
# def updateAccount():
#     if not current_user.is_authenticated():
#         return redirect(url_for('users.login'))
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username= current_user.username).first()
#         user.username = form.username.data
#         user.email = form.email.data




@users.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash("You have successfully updated your account information", "success")
        # needed for the browser to hide the message that user needs to confirm for the POST request to be sent
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'pictures/'+ current_user.image_file)
    return render_template("account.html", title='Account', image_file = image_file, form = form)



@users.route("/user/<string:username>")
def user_posts(username):
    # one is a default page number
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_post.html", posts=posts, user=user)




@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email has been sent to to your email to reset your password', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title="Request Reset", form=form)



@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        #hash the value of the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password        
        db.session.commit()
        flash('Your password has been updated ', 'success')
        return redirect(url_for('users.login'))
    return render_template('password_reset.html',title="Reset Password", form=form, user=user)
