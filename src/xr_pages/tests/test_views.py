from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest
from wagtail.core.models import Page, Site, GroupPagePermission


class BaseWebTest(WebTest):
    def setUp(self):
        moderators_group = Group.objects.get(name="Overall Site Moderators")
        self.user = G(get_user_model(), is_staff=True)
        self.user.groups.set([moderators_group])

    def test_homepage_responds(self):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "XR de")
        self.assertContains(response, "rebellion")

    def test_admin_requires_authorization(self):
        response = self.app.get(reverse("admin:index"))

        login_url = "{}?next={}".format(reverse("admin:login"), reverse("admin:index"))
        self.assertRedirects(response, login_url)

    def test_admin_authenticated_user_has_access(self):
        response = self.app.get(reverse("admin:index"), user=self.user)

        self.assertEqual(response.status_code, 200)

    def test_wagtail_admin_requires_authorization(self):
        response = self.app.get(reverse("wagtailadmin_home"))

        login_url = "{}?next={}".format(
            reverse("wagtailadmin_login"), reverse("wagtailadmin_home")
        )
        self.assertRedirects(response, login_url)

    def test_wagtail_admin_authenticated_user_has_access(self):
        response = self.app.get(reverse("wagtailadmin_home"), user=self.user)

        self.assertEqual(response.status_code, 200)
