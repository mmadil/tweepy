# imports
import datetime
from functools import wraps
from flask import (flash, redirect, render_template,
    request, session, url_for, Blueprint)

from .forms import PostTweetForm
from project import db
from project.models import Tweet

# config
tweets_blueprint = Blueprint('tweets', __name__)

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return (redirect(url_for('users.login')))
    return wrap

# tweets removed are not visible
def all_tweets():
    return db.session.query(Tweet).order_by(Tweet.posted.desc())

# routes
@tweets_blueprint.route('/tweets/')
@login_required
def tweet():
    return render_template(
        'tweets.html',
        form=PostTweetForm(),
        all_tweets=all_tweets(),
    )

@tweets_blueprint.route('/tweets/post/', methods=['GET', 'POST'])
@login_required
def post_tweet():
    error = None
    form = PostTweetForm()
    if request.method == 'POST':
        new_tweet = Tweet(
            form.tweet.data,
            datetime.datetime.now(),
            session['user_id']
        )
        db.session.add(new_tweet)
        db.session.commit()
        flash('New tweet has been posted.')
        return redirect(url_for('tweets.tweet'))
    else:
        return render_template(
            'tweets.html',
            form=form,
            error=error,
            all_tweets=all_tweets()
        )
