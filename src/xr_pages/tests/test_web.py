from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest
from wagtail.contrib.modeladmin.helpers import AdminURLHelper

from xr_pages.models import LocalGroup
from xr_pages.services import get_auth_group_name, PAGE_MODERATORS_SUFFIX
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


class LocalGroupAdminTest(PagesBaseTest, WebTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self.admin_url_helper = AdminURLHelper(model=LocalGroup)

        site_moderators_group = Group.objects.get(name="Overall Site Moderators")
        self.site_moderator = G(get_user_model(), is_staff=True)
        self.site_moderator.groups.set([site_moderators_group])

        local_group_moderators_group = Group.objects.get(
            name=get_auth_group_name(self.local_group.name, PAGE_MODERATORS_SUFFIX)
        )
        self.local_group_moderator = G(get_user_model(), is_staff=True)
        self.local_group_moderator.groups.set([local_group_moderators_group])

        regional_group_moderators_group = Group.objects.get(
            name=get_auth_group_name(self.regional_group.name, PAGE_MODERATORS_SUFFIX)
        )
        self.regional_group_moderator = G(get_user_model(), is_staff=True)
        self.regional_group_moderator.groups.set([regional_group_moderators_group])

    def test_local_group_moderator_can_view_local_group_index(self):
        list_url = self.admin_url_helper.get_action_url("index")

        page = self.app.get(list_url, user=self.local_group_moderator)
        self.assertContains(page, self.local_group.name)
        self.assertContains(page, self.regional_group.name)

    def test_local_group_moderator_can_change_local_group(self):
        list_url = self.admin_url_helper.get_action_url("index")
        edit_url = self.admin_url_helper.get_action_url("edit", self.local_group.pk)

        list_page = self.app.get(list_url, user=self.local_group_moderator)
        page = list_page.click(href=edit_url)

        self.assertContains(page, self.local_group.name)
        self.assertNotContains(page, self.regional_group.name)

        form = page.forms[1]
        form["location"] = "Somewhere between trees and water."
        response = form.submit()

        self.assertRedirects(response, list_url)

        list_page = response.follow()
        self.assertContains(list_page, "Somewhere between trees and water.")

    def test_local_group_moderator_can_not_change_regional_group(self):
        list_url = self.admin_url_helper.get_action_url("index")
        edit_url = self.admin_url_helper.get_action_url("edit", self.regional_group.pk)

        list_page = self.app.get(list_url, user=self.local_group_moderator)
        self.assertNotContains(list_page, edit_url)

        page = self.app.get(edit_url, user=self.local_group_moderator, status=403)
        self.assertEqual(page.status_code, 403)

    def test_regional_group_moderator_can_view_local_group_index(self):
        list_url = self.admin_url_helper.get_action_url("index")

        page = self.app.get(list_url, user=self.regional_group_moderator)
        self.assertContains(page, self.local_group.name)
        self.assertContains(page, self.regional_group.name)

    def test_site_moderator_can_view_local_group_index(self):
        list_url = self.admin_url_helper.get_action_url("index")

        page = self.app.get(list_url, user=self.site_moderator)
        self.assertContains(page, self.local_group.name)
        self.assertContains(page, self.regional_group.name)

    def test_site_moderator_can_change_local_and_regional_group(self):
        list_url = self.admin_url_helper.get_action_url("index")

        list_page = self.app.get(list_url, user=self.site_moderator)

        local_edit_url = self.admin_url_helper.get_action_url(
            "edit", self.local_group.pk
        )
        local_edit_page = list_page.click(href=local_edit_url)
        self.assertContains(local_edit_page, self.local_group.name)
        self.assertNotContains(local_edit_page, self.regional_group.name)

        regional_edit_url = self.admin_url_helper.get_action_url(
            "edit", self.regional_group.pk
        )
        regional_edit_page = list_page.click(href=regional_edit_url)
        self.assertContains(regional_edit_page, self.regional_group.name)
        self.assertNotContains(regional_edit_page, self.local_group.name)
