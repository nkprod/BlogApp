import os, binascii
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from application import app, db, bcrypt
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from application.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title = 'About')


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


# @app.route("/updateAccount", methods=['GET', 'POST'])
# def updateAccount():
#     if not current_user.is_authenticated():
#         return redirect(url_for('login'))
#     form = UpdateAccountForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username= current_user.username).first()
#         user.username = form.username.data
#         user.email = form.email.data




@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    # file_name = secrets.token_hex(8)
    file_name = binascii.b2a_hex(os.urandom(16)).decode('utf-8')
    _, file_ext = os.path.splitext(form_picture.filename)
    new_img_fn = file_name + file_ext
    path_to_img = os.path.join(app.root_path, 'static/pictures', new_img_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(path_to_img)
    return new_img_fn


@app.route("/account", methods=['GET', 'POST'])
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
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename = 'pictures/'+ current_user.image_file)
    return render_template("account.html", title='Account', image_file = image_file, form = form)


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been successfully added', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title="News Post", form = form)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)