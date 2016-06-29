import os
import unittest

from project import app, db
from project._config import BASE_DIR
from project.models import User

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


    # helper functions

    def login(self, name, password):
        return self.app.post('/', data=dict(
            name=name, password=password
        ), follow_redirects=True)


    # tests

    def test_404_error(self):
        response = self.app.get('/this-route-does-not-exist')
        self.assertEquals(response.status_code, 404)
        self.assertIn(b'Sorry. There is nothing here.', response.data)

'''
    def test_500_error(self):
        bad_user = User(
            name='Jaime',
            email='jaime@gameofthrones.com',
            password='cersei123'
        )
        db.session.add(bad_user)
        db.session.commit()
        response = self.login('Jaime', 'cersei123')
        self.assertEquals(response.status_code, 500)
        self.assertNotIn(b'ValueError: Invalid salt', response.data)
        self.assertIn(b'Something went terribly wrong.', response.data)
'''

if __name__ == "__main__":
    unittest.main()
