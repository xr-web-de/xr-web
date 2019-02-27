from django.contrib.auth import get_user_model
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest


class BaseWebTest(WebTest):
    def setUp(self):
        self.user = G(get_user_model(), is_staff=True)

    def test_homepage_responds(self):
        response = self.app.get(reverse("admin:login"))

        self.assertEqual(response.status_code, 200)

    def test_admin_requires_authorization(self):
        response = self.app.get(reverse("admin:index"))

        login_url = "{}?next={}".format(reverse("admin:login"), reverse("admin:index"))
        self.assertRedirects(response, login_url)

    def test_admin_authenticated_user_has_access(self):
        response = self.app.get(reverse("admin:index"), user=self.user)

        self.assertEqual(response.status_code, 200)
