from django.contrib.auth import get_user_model
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest


class BaseWebTest(WebTest):
    def setUp(self):
        self.user = G(get_user_model(), is_superuser=True, is_staff=True)

    def test_homepage_responds(self):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "extinction")
        self.assertContains(response, "rebellion")

    def test_admin_requires_authorization(self):
        response = self.app.get(reverse("admin:index"))

        login_url = "{}?next=/admin/".format(reverse("admin:login"))
        self.assertRedirects(response, login_url)

    def test_user_login(self):
        response = self.app.get(reverse("admin:index"), user=self.user)

        self.assertEqual(response.status_code, 200)
