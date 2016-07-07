from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class PostTweetForm(Form):
    tweet = StringField(
        'Tweet',
        validators=[DataRequired(), Length(min=6, max=140)]
    )
