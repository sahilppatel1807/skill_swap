import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from config import TestConfig
from __init__ import create_app, db
from models import User, Skill, make_avatar_initials, normalize_avatar_initials


class UserModelTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User(name='Test User', email='test@test.com', nickname='testuser')
        user.set_password('password123')
        self.assertTrue(user.check_password('password123'))

    def test_wrong_password_rejected(self):
        user = User(name='Test User', email='test@test.com', nickname='testuser')
        user.set_password('password123')
        self.assertFalse(user.check_password('wrongpassword'))

    def test_user_saved_to_db(self):
        user = User(name='Alice', email='alice@test.com', nickname='alice')
        user.set_password('pass1234')
        db.session.add(user)
        db.session.commit()
        fetched = User.query.filter_by(email='alice@test.com').first()
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.name, 'Alice')

    def test_duplicate_email_rejected(self):
        from sqlalchemy.exc import IntegrityError
        user1 = User(name='Alice', email='same@test.com', nickname='alice1')
        user1.set_password('pass1234')
        db.session.add(user1)
        db.session.commit()
        user2 = User(name='Bob', email='same@test.com', nickname='bob1')
        user2.set_password('pass5678')
        db.session.add(user2)
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_skill_linked_to_user(self):
        user = User(name='Bob', email='bob@test.com', nickname='bob')
        user.set_password('pass1234')
        db.session.add(user)
        db.session.commit()
        skill = Skill(user_id=user.id, name='Python', category='Programming', level='Intermediate')
        db.session.add(skill)
        db.session.commit()
        self.assertEqual(len(user.skills), 1)
        self.assertEqual(user.skills[0].name, 'Python')

    def test_multiple_skills_per_user(self):
        user = User(name='Charlie', email='charlie@test.com', nickname='charlie')
        user.set_password('pass1234')
        db.session.add(user)
        db.session.commit()
        skill1 = Skill(user_id=user.id, name='JavaScript', category='Programming', level='Beginner')
        skill2 = Skill(user_id=user.id, name='Flask', category='Web', level='Intermediate')
        db.session.add_all([skill1, skill2])
        db.session.commit()
        self.assertEqual(len(user.skills), 2)

    def test_avatar_initials_two_names(self):
        self.assertEqual(make_avatar_initials('John Doe'), 'JD')

    def test_avatar_initials_single_name(self):
        result = make_avatar_initials('Alice')
        self.assertEqual(result, 'AL')

    def test_avatar_initials_empty(self):
        self.assertEqual(make_avatar_initials(''), '??')

    def test_normalize_avatar_initials(self):
        self.assertEqual(normalize_avatar_initials('jd', ''), 'JD')

    def test_user_repr(self):
        user = User(name='Test', email='repr@test.com', nickname='repr')
        self.assertEqual(repr(user), '<User repr@test.com>')


if __name__ == '__main__':
    unittest.main()
