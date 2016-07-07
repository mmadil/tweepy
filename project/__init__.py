import datetime

from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile('_config.py')
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

from project.users.views import users_blueprint
from project.tweets.views import tweets_blueprint

# registering blueprints
app.register_blueprint(users_blueprint)
app.register_blueprint(tweets_blueprint)


# error handlers
@app.errorhandler(404)
def not_found(e):
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n404 error at {}: {}".format(current_timestamp, r))
    return render_template('404.html'), 404


# cannot test this in development
@app.errorhandler(500) # pragma: no cover
def internal_error(e):
    db.session.rollback()
    if app.debug is not True:
        now = datetime.datetime.now()
        r = request.url
        with open('error.log', 'a') as f:
            current_timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
            f.write("\n500 error at {}: {}".format(current_timestamp, r))
    return render_template('500.html'), 500
