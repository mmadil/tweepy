from flask_wtf import Form
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired


class PostTweetForm(Form):
    tweet = StringField(
        validators=[DataRequired()]
    )
