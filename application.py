from flask import Flask, render_template, url_for
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'b7aa6f35382eaaabc1363fb6f66fcba9'


@app.route("/")
@app.route("/home")
def home():
    return render_template("hello.html")

@app.route("/about")
def about():
    return render_template("goodbye.html", title = 'About')


@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template("register.html", title = 'Register', form=form)


@app.route("/register")
def login():
    form = LoginForm()
    return render_template("login.html", title = 'Login', form=form)



if __name__ == '__main__':
    app.run(debug=True)