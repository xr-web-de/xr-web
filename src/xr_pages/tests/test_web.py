from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest

from xr_pages.tests.test_pages import PagesBaseTest


class AdminWebTest(WebTest):
    def setUp(self):
        moderators_group = Group.objects.get(name="Overall Site Moderators")
        self.user = G(get_user_model(), is_staff=True)
        self.user.groups.set([moderators_group])

    def test_wagtail_admin_requires_authorization(self):
        response = self.app.get(reverse("wagtailadmin_home"))

        login_url = "{}?next={}".format(
            reverse("wagtailadmin_login"), reverse("wagtailadmin_home")
        )
        self.assertRedirects(response, login_url)

    def test_wagtail_admin_authenticated_user_has_access(self):
        response = self.app.get(reverse("wagtailadmin_home"), user=self.user)

        self.assertEqual(response.status_code, 200)


class PagesWebTest(PagesBaseTest, WebTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()

    def test_home_page(self):
        response = self.app.get(self.home_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.home_sub_page)
        self.assertLinkExists(response, self.local_group_list_page)

    def test_home_sub_page(self):
        response = self.app.get(self.home_sub_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.home_sub_page)
        self.assertLinkExists(response, self.local_group_list_page)

    def test_local_group_list_page(self):
        response = self.app.get(self.local_group_list_page.url)
        self.assertEqual(response.status_code, 200)
        local_group_page = response.click(
            linkid="local_group_link_{}".format(self.local_group.pk)
        )
        self.assertContains(local_group_page, self.local_group_page.title)
        self.assertContains(
            response, 'href="mailto:{0}"'.format(self.local_group.email)
        )

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.local_group_list_page)
        self.assertLinkExists(response, self.local_group_page)

    def test_local_group_page(self):
        response = self.app.get(self.local_group_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.local_group_list_page)
        self.assertLinkExists(response, self.local_group_page)
        self.assertLinkExists(response, self.local_group_sub_page)

    def test_local_group_sub_page(self):
        response = self.app.get(self.local_group_sub_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.local_group_list_page)
        self.assertLinkExists(response, self.local_group_page)
        self.assertLinkExists(response, self.local_group_sub_page)

    def test_404_page(self):
        response = self.app.get("/404/", status=404)
        self.assertEqual(response.status_code, 404)
