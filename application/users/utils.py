import os, binascii
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from application import mail


def save_picture(form_picture):
    # file_name = secrets.token_hex(8)  THE WAY TO DO IT IN PYTHON 3
    file_name = binascii.b2a_hex(os.urandom(16)).decode('utf-8')
    _, file_ext = os.path.splitext(form_picture.filename)
    new_img_fn = file_name + file_ext
    path_to_img = os.path.join(current_app.root_path, 'static/pictures', new_img_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(path_to_img)
    return new_img_fn





def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = """ To reset your password, visit the following link:
    {}    

    If you did not make this request, then simply ignore this email.
    """.format(url_for('users.reset_token', token=token, _external=True))
    mail.send(msg)
    
