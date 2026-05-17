"""
SkillSwap — Selenium End-to-End Tests (core flows)
====================================================
Run (Flask starts automatically on port 5001):
    python -m pytest tests/test_selenium.py -v
"""

import threading
import time
import unittest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from config import SeleniumTestConfig
from __init__ import create_app, db

BASE = "http://localhost:5001"


class SkillSwapE2ETests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # ── Flask server ──────────────────────────────────────────────────
        cls.test_app = create_app(SeleniumTestConfig)
        cls.app_context = cls.test_app.app_context()
        cls.app_context.push()
        db.create_all()

        cls.server_thread = threading.Thread(
            target=cls.test_app.run,
            kwargs={'port': 5001, 'use_reloader': False, 'debug': False}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(2)

        # ── Chrome ────────────────────────────────────────────────────────
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1280,1024')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

        # ── Seed two accounts used across all tests ───────────────────────
        cls._create_user('Alice', 'alice_e2e', 'alice@e2e.edu.au', 'AlicePass1')
        cls._create_user('Bob',   'bob_e2e',   'bob@e2e.edu.au',   'BobPass1')

        # Bob posts a skill so Alice can request it
        cls._js_login('bob@e2e.edu.au', 'BobPass1')
        cls.driver.execute_script("""
            var f = document.createElement('form');
            f.method = 'POST'; f.action = '/skills/new';
            [['name','Bob E2E Skill'],['category','Design']].forEach(function(p){
                var i = document.createElement('input');
                i.name = p[0]; i.value = p[1]; f.appendChild(i);
            });
            document.body.appendChild(f); f.submit();
        """)
        time.sleep(1)
        cls.driver.get(BASE + '/logout')
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.driver.delete_all_cookies()

    # ── Class-level helpers ───────────────────────────────────────────────

    @classmethod
    def _create_user(cls, name, nickname, email, password):
        cls.driver.get(BASE + '/signup')
        cls.driver.find_element(By.NAME, 'name').send_keys(name)
        cls.driver.find_element(By.NAME, 'nickname').send_keys(nickname)
        cls.driver.find_element(By.NAME, 'email').send_keys(email)
        cls.driver.find_element(By.NAME, 'password').send_keys(password)
        cls.driver.find_element(By.NAME, 'confirm_password').send_keys(password)
        btn = cls.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        cls.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", btn)
        time.sleep(1)

    @classmethod
    def _js_login(cls, email, password):
        cls.driver.get(BASE + '/login')
        cls.driver.execute_script(f"""
            document.querySelector('[name=identifier]').value = '{email}';
            document.querySelector('[name=password]').value = '{password}';
            document.getElementById('loginForm').submit();
        """)
        WebDriverWait(cls.driver, 8).until(lambda d: 'login' not in d.current_url)

    def _login(self, email, password):
        self._js_login(email, password)

    # ═══════════════════════════════════════════════════════════════════════
    # REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════

    # TC1 — valid signup redirects to /login
    def test_01_valid_signup(self):
        self._create_user('New User', 'newuser99', 'new@e2e.edu.au', 'NewPass1')
        self.assertIn('login', self.driver.current_url)

    # TC8 — duplicate email shows error
    def test_02_duplicate_email_shows_error(self):
        self._create_user('Alice2', 'alice_dup', 'alice@e2e.edu.au', 'AlicePass1')
        error = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'auth-error'))
        )
        self.assertIn('already exists', error.text)

    # ═══════════════════════════════════════════════════════════════════════
    # LOGIN
    # ═══════════════════════════════════════════════════════════════════════

    # TC15 — correct credentials redirect away from /login
    def test_03_login_valid_credentials(self):
        self._login('alice@e2e.edu.au', 'AlicePass1')
        self.assertNotIn('login', self.driver.current_url)

    # TC18 — wrong password shows error
    def test_04_login_invalid_credentials(self):
        self.driver.get(BASE + '/login')
        self.driver.execute_script("""
            document.querySelector('[name=identifier]').value = 'alice@e2e.edu.au';
            document.querySelector('[name=password]').value = 'WrongPass9';
            document.getElementById('loginForm').submit();
        """)
        error = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'auth-error'))
        )
        self.assertIn('Invalid', error.text)

    # TC25 — unauthenticated access to /skills redirects to login
    def test_05_protected_route_redirects(self):
        self.driver.get(BASE + '/skills')
        WebDriverWait(self.driver, 5).until(EC.url_contains('login'))
        self.assertIn('login', self.driver.current_url)

    # ═══════════════════════════════════════════════════════════════════════
    # SKILLS
    # ═══════════════════════════════════════════════════════════════════════

    # Skill TC1 — posted skill appears in the browse grid
    def test_06_add_skill_appears_in_grid(self):
        self._login('alice@e2e.edu.au', 'AlicePass1')
        self.driver.execute_script("""
            var f = document.createElement('form');
            f.method = 'POST'; f.action = '/skills/new';
            [['name','Alice E2E Skill'],['category','Programming']].forEach(function(p){
                var i = document.createElement('input');
                i.name = p[0]; i.value = p[1]; f.appendChild(i);
            });
            document.body.appendChild(f); f.submit();
        """)
        time.sleep(1)
        self.driver.get(BASE + '/skills')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.skills-grid'))
        )
        names = [c.text for c in self.driver.find_elements(By.CSS_SELECTOR, '.skill-name')]
        self.assertIn('Alice E2E Skill', names)

    # ═══════════════════════════════════════════════════════════════════════
    # REQUESTS
    # ═══════════════════════════════════════════════════════════════════════

    # TC7 — request button changes to "Requested" after clicking
    def test_07_send_request_updates_button(self):
        self._login('alice@e2e.edu.au', 'AlicePass1')
        self.driver.get(BASE + '/skills')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.skills-grid'))
        )
        for card in self.driver.find_elements(By.CSS_SELECTOR, '.skill-card'):
            try:
                if card.find_element(By.CSS_SELECTOR, '.skill-name').text == 'Bob E2E Skill':
                    card.find_element(By.CSS_SELECTOR, '.request-btn').click()
                    time.sleep(1)
                    break
            except NoSuchElementException:
                continue
        self.driver.get(BASE + '/skills')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.skills-grid'))
        )
        for card in self.driver.find_elements(By.CSS_SELECTOR, '.skill-card'):
            try:
                if card.find_element(By.CSS_SELECTOR, '.skill-name').text == 'Bob E2E Skill':
                    self.assertIn('Requested',
                                  card.find_element(By.CSS_SELECTOR, '.request-btn').text)
                    return
            except NoSuchElementException:
                continue
        self.fail("'Bob E2E Skill' card not found after requesting")

    # TC8 — own skill shows disabled "Your Skill" button
    def test_08_own_skill_button_disabled(self):
        self._login('bob@e2e.edu.au', 'BobPass1')
        self.driver.get(BASE + '/skills')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.skills-grid'))
        )
        for card in self.driver.find_elements(By.CSS_SELECTOR, '.skill-card'):
            try:
                if card.find_element(By.CSS_SELECTOR, '.skill-name').text == 'Bob E2E Skill':
                    btn = card.find_element(By.CSS_SELECTOR, 'button[disabled]')
                    self.assertIn('Your Skill', btn.text)
                    return
            except NoSuchElementException:
                continue
        self.fail("Own skill card not found")

    # TC10 — Bob accepts Alice's request, badge shows "Accepted"
    def test_09_accept_request_shows_badge(self):
        self._login('bob@e2e.edu.au', 'BobPass1')
        self.driver.get(BASE + '/requests')
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.btn-accept'))
        )
        self.driver.find_element(By.CSS_SELECTOR, '.btn-accept').click()
        time.sleep(1)
        self.driver.get(BASE + '/requests')
        badge = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.badge-accepted'))
        )
        self.assertEqual(badge.text, 'Accepted')

    # ═══════════════════════════════════════════════════════════════════════
    # CHAT
    # ═══════════════════════════════════════════════════════════════════════

    # TC_C — chat page loads and accepted connection appears in sidebar
    def test_10_chat_page_shows_connection(self):
        self._login('alice@e2e.edu.au', 'AlicePass1')
        self.driver.get(BASE + '/chat')

        # Connection item should appear after Bob accepted Alice's request
        conn = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.connection-item'))
        )
        self.assertTrue(conn.is_displayed())
        self.assertIn('bob_e2e', conn.text)


if __name__ == '__main__':
    unittest.main(verbosity=2)