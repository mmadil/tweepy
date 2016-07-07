import datetime

from project import db


class Tweet(db.Model):
    __tablename__ = 'tweets'

    tweet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tweet = db.Column(db.String, nullable=False)
    posted = db.Column(db.DateTime, nullable=False)

    def __init__(self, tweet, posted, user_id):
        self.tweet = tweet
        self.posted = posted
        self.user_id = user_id

    def __repr__(self):
        return '<Id {0} - {1}>'.format(self.tweet_id, self.tweet)


    @classmethod
    def delta_time(cls, tweet_posted):
        now = datetime.datetime.now()
        td = now - tweet_posted
        days = td.days
        hours = td.seconds//3600
        minutes = (td.seconds//60)%60
        if days > 0:
            return tweet_posted.strftime("%d %B, %Y")
        elif hours > 0:
            return str(hours) + 'h'
        elif minutes > 0:
            return str(minutes) + 'm'
        else:
            return 'few seconds ago'



class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    tweets = db.relationship('Tweet', backref='poster')
    role = db.Column(db.String, default='user')

    def __init__(self, name=None, email=None, password=None, role=None):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User {0}>'.format(self.name)

    @classmethod
    def is_following(cls, who_id, whom_id):
        whom_ids = db.session.query(Follower.whom_id).filter_by(who_id=who_id).all()
        whom_ids = [i[0] for i in whom_ids]
        if whom_id in whom_ids:
            return True
        else:
            return False


class Follower(db.Model):
    __tablename__ = 'follower'
    __table_args__ = (
        db.PrimaryKeyConstraint('who_id', 'whom_id'),
    )

    who_id = db.Column(db.Integer)
    whom_id = db.Column(db.Integer)


    def __init__(self, who_id, whom_id):
        self.who_id = who_id
        self.whom_id = whom_id

    def __repr__(self):
        return '<User {0} follows {1}>'.format(self.who_id, self.whom_id)
