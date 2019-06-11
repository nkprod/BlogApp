import os

class Config:
    SECRET_KEY = 'b7aa6f35382eaaabc1363fb6f66fcba9'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    # if values are hardcoded, valid email and password should be used
    MAIL_USERNAME = "os.environ.get('EMAIL_USER')"
    MAIL_PASSWORD = "os.environ.get('MAIL_PASSWORD')"