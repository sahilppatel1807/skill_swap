import unittest
import json
from config import TestConfig
from __init__ import create_app, db
from models import User, Skill, Request, Message, normalize_avatar_initials


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_user(name='Alice', email='alice@test.com', nickname='alice', password='Pass1234'):
    u = User(name=name, email=email, nickname=nickname,
             avatar_initials=normalize_avatar_initials(nickname, name))
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u

def make_skill(user_id, name='Python', category='Programming'):
    s = Skill(user_id=user_id, name=name, category=category)
    db.session.add(s)
    db.session.commit()
    return s


# ── Base ──────────────────────────────────────────────────────────────────────

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['RATELIMIT_ENABLED'] = False
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, identifier='alice@test.com', password='Pass1234'):
        return self.client.post('/login', data={
            'identifier': identifier, 'password': password
        }, follow_redirects=True)

    def logout(self):
        self.client.get('/logout', follow_redirects=True)


# ═════════════════════════════════════════════════════════════════════════════
# 1 — REGISTRATION
# ═════════════════════════════════════════════════════════════════════════════

class RegistrationTests(BaseTestCase):

    # TC1 — valid signup saves user and redirects
    def test_valid_signup(self):
        self.client.post('/signup', data={
            'name': 'Alice Smith', 'nickname': 'alice',
            'email': 'alice@uwa.edu.au',
            'password': 'Pass1234', 'confirm_password': 'Pass1234',
        })
        self.assertIsNotNone(User.query.filter_by(email='alice@uwa.edu.au').first())

    def test_non_student_email_rejected(self):
        rv = self.client.post('/signup', data={
            'name': 'Alice Smith', 'nickname': 'alice',
            'email': 'alice@test.com',
            'password': 'Pass1234', 'confirm_password': 'Pass1234',
        })
        self.assertIsNone(User.query.filter_by(email='alice@test.com').first())
        self.assertIn(b'.edu.au', rv.data)

    # TC7 — mismatched passwords rejected
    def test_password_mismatch_rejected(self):
        self.client.post('/signup', data={
            'name': 'Alice', 'nickname': 'alice', 'email': 'alice@uwa.edu.au',
            'password': 'Pass1234', 'confirm_password': 'Pass9999',
        })
        self.assertIsNone(User.query.filter_by(email='alice@uwa.edu.au').first())

    # TC8 — duplicate email rejected
    def test_duplicate_email_rejected(self):
        make_user(email='alice@uwa.edu.au')
        rv = self.client.post('/signup', data={
            'name': 'Alice2', 'nickname': 'alice2', 'email': 'alice@uwa.edu.au',
            'password': 'Pass1234', 'confirm_password': 'Pass1234',
        })
        self.assertIn(b'already exists', rv.data)

    # TC9 — duplicate nickname rejected
    def test_duplicate_nickname_rejected(self):
        make_user()
        rv = self.client.post('/signup', data={
            'name': 'Alice2', 'nickname': 'alice', 'email': 'other@curtin.edu.au',
            'password': 'Pass1234', 'confirm_password': 'Pass1234',
        })
        self.assertIn(b'already taken', rv.data)


# ═════════════════════════════════════════════════════════════════════════════
# 2 — LOGIN
# ═════════════════════════════════════════════════════════════════════════════

class LoginTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        make_user()

    # TC15/16 — login with email and nickname both work
    def test_login_with_email(self):
        rv = self.login('alice@test.com', 'Pass1234')
        self.assertNotIn(b'Invalid', rv.data)

    def test_login_with_nickname(self):
        rv = self.login('alice', 'Pass1234')
        self.assertNotIn(b'Invalid', rv.data)

    # TC18 — wrong password rejected
    def test_wrong_password_rejected(self):
        rv = self.login('alice@test.com', 'WrongPass1')
        self.assertIn(b'Invalid', rv.data)

    # TC17 — session cleared after logout
    def test_logout_clears_session(self):
        self.login()
        self.logout()
        rv = self.client.get('/skills', follow_redirects=False)
        self.assertEqual(rv.status_code, 302)


# ═════════════════════════════════════════════════════════════════════════════
# 3 — SKILLS
# ═════════════════════════════════════════════════════════════════════════════

class SkillsTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user = make_user()
        self.login()

    # Skill TC1 — add skill successfully
    def test_add_skill(self):
        self.client.post('/skills/new', data={
            'name': 'Django', 'category': 'Programming'
        }, follow_redirects=True)
        self.assertIsNotNone(Skill.query.filter_by(name='Django').first())

    # Skill TC2 — empty name rejected
    def test_empty_skill_name_rejected(self):
        self.client.post('/skills/new', data={
            'name': '', 'category': 'Programming'
        }, follow_redirects=True)
        self.assertEqual(Skill.query.count(), 0)

    # Skill TC6 — unauthenticated access redirects
    def test_unauthenticated_redirects(self):
        self.logout()
        rv = self.client.get('/skills', follow_redirects=False)
        self.assertEqual(rv.status_code, 302)


# ═════════════════════════════════════════════════════════════════════════════
# 4 — REQUESTS
# ═════════════════════════════════════════════════════════════════════════════

class RequestsTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.alice = make_user()
        self.bob   = make_user(name='Bob', email='bob@test.com',
                               nickname='bob', password='Pass5678')
        self.skill = make_skill(user_id=self.bob.id)

    def login_as(self, email, password):
        self.client.post('/login', data={
            'identifier': email, 'password': password
        }, follow_redirects=True)

    # TC7 — send request creates pending entry
    def test_send_request(self):
        self.login_as('alice@test.com', 'Pass1234')
        self.client.post('/request_skill', data={'skill_id': self.skill.id})
        req = Request.query.filter_by(from_user_id=self.alice.id).first()
        self.assertIsNotNone(req)
        self.assertEqual(req.status, 'pending')

    # TC8 — cannot request own skill
    def test_cannot_request_own_skill(self):
        self.login_as('bob@test.com', 'Pass5678')
        rv = self.client.post('/request_skill', data={'skill_id': self.skill.id})
        self.assertEqual(rv.status_code, 400)

    # TC9 — duplicate request rejected
    def test_duplicate_request_rejected(self):
        self.login_as('alice@test.com', 'Pass1234')
        self.client.post('/request_skill', data={'skill_id': self.skill.id})
        rv = self.client.post('/request_skill', data={'skill_id': self.skill.id})
        self.assertEqual(rv.status_code, 400)

    # TC10 — accept request changes status
    def test_accept_request(self):
        self.login_as('alice@test.com', 'Pass1234')
        self.client.post('/request_skill', data={'skill_id': self.skill.id})
        req = Request.query.filter_by(from_user_id=self.alice.id).first()
        self.client.get('/logout', follow_redirects=True)

        self.login_as('bob@test.com', 'Pass5678')
        self.client.post(f'/requests/accept/{req.id}',
                         content_type='application/json')
        db.session.refresh(req)
        self.assertEqual(req.status, 'accepted')

    def test_accepting_one_skill_accepts_other_pending_from_same_user(self):
        skill2 = make_skill(user_id=self.bob.id, name='React', category='Programming')
        self.login_as('alice@test.com', 'Pass1234')
        self.client.post('/request_skill', data={'skill_id': self.skill.id})
        self.client.post('/request_skill', data={'skill_id': skill2.id})
        req1 = Request.query.filter_by(skill_id=self.skill.id).first()
        req2 = Request.query.filter_by(skill_id=skill2.id).first()
        self.client.get('/logout', follow_redirects=True)

        self.login_as('bob@test.com', 'Pass5678')
        self.client.post(f'/requests/accept/{req1.id}')
        db.session.refresh(req1)
        db.session.refresh(req2)
        self.assertEqual(req1.status, 'accepted')
        self.assertEqual(req2.status, 'accepted')

    def test_connected_user_shows_accepted_on_all_skills(self):
        skill2 = make_skill(user_id=self.bob.id, name='React', category='Programming')
        req = Request(
            skill_id=self.skill.id,
            from_user_id=self.alice.id,
            to_user_id=self.bob.id,
            status='accepted',
        )
        pending = Request(
            skill_id=skill2.id,
            from_user_id=self.alice.id,
            to_user_id=self.bob.id,
            status='pending',
        )
        db.session.add_all([req, pending])
        db.session.commit()

        self.login_as('alice@test.com', 'Pass1234')
        rv = self.client.get('/skills')
        self.assertEqual(rv.status_code, 200)
        self.assertIn(b'Accepted', rv.data)
        self.assertNotIn(b'Requested', rv.data)

    def test_cannot_request_another_skill_when_already_connected(self):
        db.session.add(Request(
            skill_id=self.skill.id,
            from_user_id=self.alice.id,
            to_user_id=self.bob.id,
            status='accepted',
        ))
        db.session.commit()
        skill2 = make_skill(user_id=self.bob.id, name='React', category='Programming')

        self.login_as('alice@test.com', 'Pass1234')
        rv = self.client.post('/request_skill', data={'skill_id': skill2.id})
        self.assertEqual(rv.status_code, 400)
        self.assertIn(b'Already connected', rv.data)


# ═════════════════════════════════════════════════════════════════════════════
# 5 — CHAT
# ═════════════════════════════════════════════════════════════════════════════

class ChatTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.alice = make_user()
        self.bob   = make_user(name='Bob', email='bob@test.com',
                               nickname='bob', password='Pass5678')
        skill = make_skill(user_id=self.bob.id)
        conn = Request(skill_id=skill.id, from_user_id=self.alice.id,
                       to_user_id=self.bob.id, status='accepted')
        db.session.add(conn)
        db.session.commit()
        self.client.post('/login', data={
            'identifier': 'alice@test.com', 'password': 'Pass1234'
        }, follow_redirects=True)

    # TC13 — send message successfully
    def test_send_message(self):
        rv = self.client.post('/chat/send',
            data=json.dumps({'user_id': self.bob.id, 'message': 'Hello!'}),
            content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(Message.query.count(), 1)

    # TC14 — empty message rejected
    def test_empty_message_rejected(self):
        rv = self.client.post('/chat/send',
            data=json.dumps({'user_id': self.bob.id, 'message': '   '}),
            content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        self.assertEqual(Message.query.count(), 0)

    # TC17 — no connection → 403
    def test_no_connection_rejected(self):
        charlie = make_user(name='Charlie', email='charlie@test.com',
                            nickname='charlie', password='Pass9999')
        rv = self.client.get(f'/chat/messages/{charlie.id}')
        self.assertEqual(rv.status_code, 403)

    # TC16 — message history loads correctly
    def test_message_history(self):
        db.session.add(Message(sender_id=self.alice.id,
                               receiver_id=self.bob.id, body='Hi Bob!'))
        db.session.commit()
        rv = self.client.get(f'/chat/messages/{self.bob.id}')
        data = json.loads(rv.data)
        self.assertEqual(data['messages'][0]['text'], 'Hi Bob!')


if __name__ == '__main__':
    unittest.main(verbosity=2)