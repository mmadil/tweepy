import os
import unittest

from project import app, db
from project._config import BASE_DIR
from project.models import User, Follower

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

    # tests

    def test_user_can_register(self):
        new_user = User('foobar', 'foobar@example.com', 'barfoo', 'barfoo')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.name
            assert t.name == 'foobar'

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foobar', 'barfoo')
        self.assertIn(b'Invalid username or password', response.data)

    def test_users_can_login(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        response = self.login('foobar', 'barfoo')
        self.assertIn(b'Welcome', response.data)

    def test_logged_in_users_cannot_visit_register_page(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.app.get('register/', follow_redirects=True)
        self.assertNotIn(b'Already registered?', response.data)

    def test_invalid_form_data(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        response = self.login('alert("alert box!")', 'barfoo')
        self.assertIn(b'Invalid username or password', response.data)

    def test_user_registeration(self):
        self.app.get('register', follow_redirects=True)
        response = self.register(
            'foobar', 'foobar@example.com','barfoo', 'barfoo'
        )
        self.assertIn(b'Thanks for registering. Plese login.', response.data)

    def test_duplicate_user_registeration_throws_error(self):
        self.app.get('register/', follow_redirects=True)
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.app.get('register/', follow_redirects=True)
        response = self.register(
            'foobar', 'foobar@example.com','barfoo', 'barfoo'
        )
        self.assertIn(
            b'That username and/or email already exists.', response.data
        )

    def test_logged_in_users_can_logout(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.login('foobar', 'barfoo')
        response = self.logout()
        self.assertIn(b'You have been logged out', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'You have been logged out', response.data)

    def test_users_page_shows_all_the_users(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com','foobar', 'foobar')
        self.login('barfoo', 'foobar')
        response = self.app.get('users/', follow_redirects=True)
        self.assertIn(b'foobar', response.data)
        self.assertIn(b'barfoo', response.data)

    def test_is_following_fuctionality(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com','foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/follow/2/', follow_redirects=True)
        user = db.session.query(User).first()
        self.assertTrue(user.is_following(1, 2))
        self.assertFalse(user.is_following(1, 1))

    def test_string_representation_of_the_user_obeject(self):
        db.session.add(
            User(
                'foobar',
                'foobar@example.com',
                'barfoo'
            )
        )
        db.session.commit()
        users = db.session.query(User).all()
        for user in users:
            self.assertEqual(str(user), '<User {}>'.format(user.name))

    def test_string_representation_of_the_follower_object(self):
        self.register('foobar', 'foobar@example.com','barfoo', 'barfoo')
        self.register('barfoo', 'barfoo@example.com','foobar', 'foobar')
        self.login('foobar', 'barfoo')
        self.app.get('tweets/follow/2/', follow_redirects=True)
        follower = db.session.query(Follower).first()
        self.assertEqual(str(follower), '<User {0} follows {1}>'.format('1', '2'))


if __name__ == "__main__":
    unittest.main()
