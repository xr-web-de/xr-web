import unittest
from contextlib import contextmanager

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


@unittest.skipIf(
    settings.SKIP_SELENIUM, "Selenium tests disabled, settings.SKIP_SELENIUM = True"
)
class SeleniumTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        # Without this, headless chromium won't start in our gitlab ci
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920x1080")
        cls.driver = webdriver.Chrome(options=options)
        cls.implicit_wait_time = 10
        cls.driver.implicitly_wait(cls.implicit_wait_time)
        super(SeleniumTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super(SeleniumTest, cls).tearDownClass()

    @contextmanager
    def disable_implicit_wait(self):
        self.driver.implicitly_wait(0)
        yield
        self.driver.implicitly_wait(self.implicit_wait_time)

    def setUp(self):
        self.user = get_user_model().objects.create(
            username="test", email="test@example.com"
        )
        self.user.set_password("test")
        self.user.save()

    def __init__(self, *args, **kwargs):
        super(SeleniumTest, self).__init__(*args, **kwargs)

    def login(self):
        self.driver.get("%s%s" % (self.live_server_url, "/accounts/login/"))

        username_input = self.driver.find_element_by_name("login-username")
        username_input.send_keys("test@example.com")

        password_input = self.driver.find_element_by_name("login-password")
        password_input.send_keys("test")

        self.driver.find_element_by_name("login_submit").click()

    def assertTextExists(self, text, timeout=10):
        def text_exist(driver):
            try:
                body = driver.find_element_by_tag_name("body")
            except NoSuchElementException:
                return False
            return text in body.text

        wait = WebDriverWait(self.driver, timeout)
        wait.until(text_exist, u"AssertionError: Text '%s' not found in body" % (text,))

    def assertNotTextExists(self, text, timeout=10):
        def text_does_not_exist(driver):
            try:
                body = driver.find_element_by_tag_name("body")
            except NoSuchElementException:
                return False
            exists = text in body.text
            return not exists

        wait = WebDriverWait(self.driver, timeout)
        wait.until(
            text_does_not_exist, u"AssertionError: Text '%s' found in body" % (text,)
        )

    def assertTextIn(self, text, css_selector, timeout=10):
        def text_in(driver):
            try:
                container = driver.find_element_by_css_selector(css_selector)
            except NoSuchElementException:
                return False
            return text in container.text

        wait = WebDriverWait(self.driver, timeout)
        wait.until(text_in, u"AssertionError: Text '%s' not found in body" % (text,))
