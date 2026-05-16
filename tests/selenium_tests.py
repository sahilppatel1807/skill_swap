import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config import SeleniumTestConfig
from __init__ import create_app, db
from models import User

LOCAL_HOST = "http://localhost:5001/"


class SeleniumTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
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

        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1280,1024')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(5)

        # Create test user via the signup form so server can see it
        cls.driver.get(LOCAL_HOST + 'signup')
        cls.driver.find_element(By.NAME, 'name').send_keys('Test User')
        cls.driver.find_element(By.NAME, 'nickname').send_keys('seleniumuser')
        cls.driver.find_element(By.NAME, 'email').send_keys('selenium@test.com')
        cls.driver.find_element(By.NAME, 'password').send_keys('Test1234')
        cls.driver.find_element(By.NAME, 'confirm_password').send_keys('Test1234')
        btn = cls.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        cls.driver.execute_script("arguments[0].scrollIntoView(true); arguments[0].click();", btn)
        time.sleep(2)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        self.driver.delete_all_cookies()

    # ── Tests ──────────────────────────────────────────────────────────

    def test_login_page_loads(self):
        self.driver.get(LOCAL_HOST + 'login')
        self.assertIn('SkillSwap', self.driver.title)
        self.assertTrue(self.driver.find_element(By.NAME, 'identifier').is_displayed())
        self.assertTrue(self.driver.find_element(By.NAME, 'password').is_displayed())

    def test_signup_page_loads(self):
        self.driver.get(LOCAL_HOST + 'signup')
        self.assertIn('SkillSwap', self.driver.title)
        self.assertTrue(self.driver.find_element(By.NAME, 'name').is_displayed())
        self.assertTrue(self.driver.find_element(By.NAME, 'email').is_displayed())
        self.assertTrue(self.driver.find_element(By.NAME, 'password').is_displayed())

    def test_login_with_invalid_credentials(self):
        self.driver.get(LOCAL_HOST + 'login')
        self.driver.execute_script("""
            document.querySelector('[name=identifier]').value = 'wrong@test.com';
            document.querySelector('[name=password]').value = 'WrongPass1';
            document.getElementById('loginForm').submit();
        """)
        WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'auth-error'))
        )
        error = self.driver.find_element(By.CLASS_NAME, 'auth-error')
        self.assertIn('Invalid', error.text)

    def test_login_with_valid_credentials(self):
        self.driver.get(LOCAL_HOST + 'login')
        self.driver.execute_script("""
            document.querySelector('[name=identifier]').value = 'selenium@test.com';
            document.querySelector('[name=password]').value = 'Test1234';
            document.getElementById('loginForm').submit();
        """)
        WebDriverWait(self.driver, 10).until(
            lambda d: 'login' not in d.current_url
        )
        self.assertNotIn('login', self.driver.current_url)

    def test_protected_page_redirects_to_login(self):
        self.driver.get(LOCAL_HOST + 'skills')
        WebDriverWait(self.driver, 5).until(EC.url_contains('login'))
        self.assertIn('login', self.driver.current_url)

    def test_signup_link_goes_to_signup(self):
        self.driver.get(LOCAL_HOST + 'login')
        signup_link = self.driver.find_element(By.LINK_TEXT, 'Sign Up')
        self.driver.execute_script("arguments[0].click();", signup_link)
        WebDriverWait(self.driver, 5).until(EC.url_contains('signup'))
        self.assertIn('signup', self.driver.current_url)

    def test_login_link_on_signup_page(self):
        self.driver.get(LOCAL_HOST + 'signup')
        login_link = self.driver.find_element(By.CSS_SELECTOR, 'a.auth-link')
        self.driver.execute_script("arguments[0].click();", login_link)
        WebDriverWait(self.driver, 5).until(EC.url_contains('login'))
        self.assertIn('login', self.driver.current_url)


if __name__ == '__main__':
    unittest.main()
