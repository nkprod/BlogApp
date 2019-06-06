import os, binascii
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from application import app, db, bcrypt, mail
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, PasswordResetForm
from application.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
@app.route("/home")
def home():
    # one is a default page number
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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
        return redirect(url_for('login'))
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
    return render_template('create_post.html', title="News Post", form = form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been successfully updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title="Update Post", form = form, legend='Update Post')



@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been successfully deleted', 'success')
    return redirect(url_for('home'))



@app.route("/user/<string:username>")
def user_posts(username):
    # one is a default page number
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_post.html", posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = """ To reset your password, visit the following link:
    {}    

    If you did not make this request, then simply ignore this email.
    """.format(url_for('reset_token', token=token, _external=True))
    mail.send(msg)
    


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email has been sent to to your email to reset your password', 'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title="Request Reset", form=form)



@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        #hash the value of the password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password        
        db.session.commit()
        flash('Your password has been updated ', 'success')
        return redirect(url_for('login'))
    return render_template('password_reset.html',title="Reset Password", form=form, user=user)
