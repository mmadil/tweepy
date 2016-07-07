import os
import unittest
from datetime import datetime
from freezegun import freeze_time

from project import app, db, bcrypt
from project._config import BASE_DIR
from project.models import User, Tweet

TEST_DB = 'test.db'

class MainTest(unittest.TestCase):

    # setup function
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(BASE_DIR, TEST_DB)
        self.app = app.test_client()
        db.create_all()

        self.assertEquals(app.debug, False)

    # teardown function
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # helper funcitons

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password), follow_redirects=True)

    def register(self, name, email, password, confirm):
        return self.app.post('register/', data=dict(
            name=name, email=email, password=password, confirm=confirm
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('logout/', follow_redirects=True)

    def create_user(self, name, email, password):
        new_user = User(
            name=name,
            email=email,
            password=bcrypt.generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

    def create_tweet(self, tweet):
        return self.app.post('tweets/post/', data=dict(
            tweet=tweet
        ), follow_redirects=True)

    # tests
    def test_logged_in_users_can_access_tweets_page(self):
        self.register(
            'foobar', 'foobar@example.com','barfoo', 'barfoo'
        )
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"What's happening?", response.data)

    def test_not_logged_in_users_cannot_access_tweets_page(self):
        response = self.app.get('tweets/', follow_redirects=True)
        self.assertIn(b'You need to login first', response.data)

    def test_users_can_add_tweets(self):
        self.create_user('foobar', 'foobar@example.com','barfoo')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/')
        response = self.create_tweet('test tweet')
        self.assertIn(b'New tweet has been posted.', response.data)
        self.assertIn(b'test tweet', response.data)

    def test_users_cannot_add_tweet_when_error(self):
        self.create_user('foobar', 'foobar@example.com','barfoo')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/', follow_redirects=True)
        response = self.app.post('tweets/post/', data=dict(
            tweet='',
            posted=datetime.now,
            user_id=1
        ), follow_redirects=True)
        self.assertIn(b'This field is required.', response.data)

    def test_users_can_delete_tweets(self):
        self.register(
            'foobar', 'foobar@example.com','barfoo', 'barfoo'
        )
        self.login('foobar', 'barfoo')
        self.create_tweet('test tweet')
        response = self.app.get('tweets/delete/1/', follow_redirects=True)
        self.assertIn(b'That tweet was deleted.', response.data)

    def test_users_can_delete_only_their_tweets(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('barfoo', 'foobar')
        self.create_tweet('test tweet')
        self.logout()
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/delete/1/', follow_redirects=True)
        self.assertIn(b'You can only delete tasks that belong to you.', response.data)

    def test_users_cannot_delete_non_existing_tweets(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/delete/1/', follow_redirects=True)
        self.assertIn(b'That tweet does not exists. Saw what you did there, Hacker!', response.data)

    def test_users_can_follow_other_users(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/follow/2/', follow_redirects=True)
        self.assertIn(b'You are now following barfoo', response.data)

    def test_users_cannot_follow_the_same_user_twice(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/follow/2/', follow_redirects=True)
        response = self.app.get('tweets/follow/2/', follow_redirects=True)
        self.assertIn(b'You are already following barfoo', response.data)

    def test_users_can_unfollow_other_users(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/follow/2/', follow_redirects=True)
        response = self.app.get('tweets/unfollow/2/', follow_redirects=True)
        self.assertIn(b'You are no more following barfoo', response.data)

    def test_users_cannot_unfollow_other_users_twice(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/follow/2/', follow_redirects=True)
        self.app.get('tweets/unfollow/2/', follow_redirects=True)
        response = self.app.get('tweets/unfollow/2/', follow_redirects=True)
        self.assertIn(b'You are not following barfoo to unfollow.', response.data)

    def test_users_cannot_follow_themselves(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/follow/1/', follow_redirects=True)
        self.assertIn(b'No use following yourself.', response.data)

    def test_users_cannot_unfollow_themselves(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/unfollow/1/', follow_redirects=True)
        self.assertIn(b'No use unfollowing yourself.', response.data)

    def test_users_cannot_follow_non_exiting_users(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/follow/2/', follow_redirects=True)
        self.assertIn(b'That user does not exist', response.data)

    def test_users_cannot_unfollow_non_exiting_users(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('tweets/unfollow/2/', follow_redirects=True)
        self.assertIn(b'That user does not exist', response.data)

    def test_user_not_following_anyone_cannot_see_others_tweets(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com', 'foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.create_tweet('test tweet from foobar')
        self.logout()
        self.login('barfoo', 'foobar')
        response = self.create_tweet('test tweet from barfoo')
        self.assertNotIn(b'test tweet from foobar', response.data)
        self.assertIn(b'test tweet from barfoo', response.data)

    def test_tweet_delta_time_func(self):
        test_time = datetime(year=2016, month=7, day=7, hour=04, minute=00, second=01)
        few_minutes_ahead = datetime(year=2016, month=7, day=7, hour=04, minute=03, second=01)
        few_hours_ahead = datetime(year=2016, month=7, day=7, hour=06, minute=03, second=01)
        few_days_ahead = datetime(year=2016, month=7, day=8, hour=04, minute=00, second=01)
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        db.session.add(
            Tweet(
                'Test tweet',
                test_time,
                1
            )
        )
        db.session.commit()
        tweet = db.session.query(Tweet).first()
        with freeze_time(test_time) as frozen_time:
            self.assertEqual('few seconds ago', Tweet.delta_time(tweet.posted))
        with freeze_time(few_minutes_ahead) as frozen_time:
            self.assertEqual('3m', Tweet.delta_time(tweet.posted))
        with freeze_time(few_hours_ahead) as frozen_time:
            self.assertEqual('2h', Tweet.delta_time(tweet.posted))
        with freeze_time(few_days_ahead) as frozen_time:
            self.assertEqual('07 July, 2016', Tweet.delta_time(tweet.posted))

    def test_string_representation_of_tweets(self):
        db.session.add(
            Tweet(
                'Test tweet for string repr.',
                datetime.now(),
                1
            )
        )
        db.session.commit()
        tweets = db.session.query(Tweet).all()
        for tweet in tweets:
            self.assertEqual(str(tweet), '<Id {0} - {1}>'.format(tweet.tweet_id, tweet.tweet))



if __name__ == "__main__":
    unittest.main()
