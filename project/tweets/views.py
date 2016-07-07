# imports
import datetime
from functools import wraps
from flask import (flash, redirect, render_template,
    request, session, url_for, Blueprint)
from sqlalchemy.exc import IntegrityError

from .forms import PostTweetForm
from project import db
from project.models import User, Tweet, Follower

# config
tweets_blueprint = Blueprint('tweets', __name__)

# helper functions

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first')
            return (redirect(url_for('users.login')))
    return wrap

def filtered_tweets(user_id):
    who_id = user_id
    whom_ids = db.session.query(Follower.whom_id).filter_by(who_id=who_id)
    user_tweets = db.session.query(Tweet).filter_by(user_id=who_id)
    if whom_ids.all():
        follower_tweets = db.session.query(Tweet).filter(Tweet.user_id.in_(whom_ids))
        result = user_tweets.union(follower_tweets)
        return result.order_by(Tweet.posted.desc())
    else:
        return user_tweets.order_by(Tweet.posted.desc())


# routes

@tweets_blueprint.route('/tweets/')
@login_required
def tweet():
    return render_template(
        'tweets.html',
        form=PostTweetForm(),
        all_tweets=filtered_tweets(session['user_id']),
    )

@tweets_blueprint.route('/tweets/post/', methods=['GET', 'POST'])
@login_required
def post_tweet():
    error = None
    form = PostTweetForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_tweet = Tweet(
                form.tweet.data,
                datetime.datetime.now(),
                session['user_id']
            )
            db.session.add(new_tweet)
            db.session.commit()
            flash('New tweet has been posted.')
            return redirect(url_for('tweets.tweet'))
    return render_template(
        'tweets.html',
        form=form,
        error=error,
        all_tweets=filtered_tweets(session['user_id']),
    )

@tweets_blueprint.route('/tweets/delete/<int:tweet_id>/')
@login_required
def delete_tweet(tweet_id):
    our_tweet_id = tweet_id
    tweet = db.session.query(Tweet).filter_by(tweet_id=our_tweet_id)
    if tweet.first():
        if session['user_id'] == tweet.first().user_id:
            tweet.delete()
            db.session.commit()
            flash('That tweet was deleted.')
            return redirect(url_for('tweets.tweet'))
        else:
            flash('You can only delete tasks that belong to you.')
            return redirect(url_for('tweets.tweet'))
    else:
        flash('That tweet does not exists. Saw what you did there, Hacker!')
        return redirect(url_for('tweets.tweet'))

@tweets_blueprint.route('/tweets/follow/<int:user_id>/')
@login_required
def follow_user(user_id):
    whom_id = user_id
    try:
        whom = db.session.query(User).filter_by(id=whom_id).first().name
        if session['user_id'] != whom_id:
            new_follow = Follower(
                session['user_id'],
                whom_id
            )
            try:
                db.session.add(new_follow)
                db.session.commit()
                flash('You are now following {}'.format(whom))
                return redirect(url_for('tweets.tweet'))
            except IntegrityError:
                flash('You are already following {}'.format(whom))
                return redirect(url_for('tweets.tweet'))
        else:
            flash('No use following yourself. You will still see your tweets anyway. :)')
            return redirect(url_for('tweets.tweet'))
    except AttributeError:
        flash('That user does not exist.')
        return redirect(url_for('tweets.tweet'))

@tweets_blueprint.route('/tweets/unfollow/<int:user_id>/')
@login_required
def unfollow_user(user_id):
    whom_id = user_id
    try:
        whom = db.session.query(User).filter_by(id=whom_id).first().name
        if session['user_id'] != whom_id:
            following = db.session.query(
                Follower).filter_by(who_id=session['user_id'], whom_id=whom_id)
            if following.all():
                following.delete()
                db.session.commit()
                flash('You are no more following {}'.format(whom))
                return redirect(url_for('tweets.tweet'))
            else:
                flash('You are not following {} to unfollow.'.format(whom))
                return redirect(url_for('tweets.tweet'))
        else:
            flash('No use unfollowing yourself. You will still see your tweets anyway. :)')
            return redirect(url_for('tweets.tweet'))
    except AttributeError:
        flash('That user does not exist.')
        return redirect(url_for('tweets.tweet'))
