from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField('Title of the post', validators=[DataRequired()])
    content = TextAreaField('Content of the post', validators=[DataRequired()])
    submit = SubmitField('Post')
 