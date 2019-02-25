from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest
from wagtail.core.models import Page, Site, GroupPagePermission


class BaseWebTest(WebTest):
    def setUp(self):
        # Create page content type
        page_content_type, created = ContentType.objects.get_or_create(
            model="page", app_label="wagtailcore"
        )

        # Create root page
        root = Page.objects.create(
            title="Root",
            slug="root",
            content_type=page_content_type,
            path="0001",
            depth=1,
            numchild=1,
            url_path="/",
        )

        # Create homepage
        homepage = Page.objects.create(
            title="extinction rebellion",
            slug="home",
            content_type=page_content_type,
            path="00010001",
            depth=2,
            numchild=0,
            url_path="/home/",
        )

        # Create default site
        Site.objects.create(
            hostname="localhost", root_page_id=homepage.id, is_default_site=True
        )

        # Create auth groups
        moderators_group = Group.objects.create(name="Moderators")
        editors_group = Group.objects.create(name="Editors")

        # Create group permissions
        GroupPagePermission.objects.create(
            group=moderators_group, page=root, permission_type="add"
        )
        GroupPagePermission.objects.create(
            group=moderators_group, page=root, permission_type="edit"
        )
        GroupPagePermission.objects.create(
            group=moderators_group, page=root, permission_type="publish"
        )

        GroupPagePermission.objects.create(
            group=editors_group, page=root, permission_type="add"
        )
        GroupPagePermission.objects.create(
            group=editors_group, page=root, permission_type="edit"
        )

        self.user = G(get_user_model(), is_staff=True)
        self.user.groups.set([moderators_group])

    def test_homepage_responds(self):
        response = self.app.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "extinction")
        self.assertContains(response, "rebellion")

    def test_admin_requires_authorization(self):
        response = self.app.get(reverse("admin:index"))

        login_url = "{}?next={}".format(reverse("admin:login"), reverse("admin:index"))
        self.assertRedirects(response, login_url)

    def test_admin_authenticated_user_has_access(self):
        response = self.app.get(reverse("admin:index"), user=self.user)

        self.assertEqual(response.status_code, 200)
