from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from django_dynamic_fixture import G
from django_webtest import WebTest
from wagtail.core.models import Site, Page, GroupPagePermission
from wagtail.tests.utils import WagtailPageTests

from xr_pages.models import (
    HomeSubPage,
    LocalGroupListPage,
    HomePage,
    LocalGroupPage,
    LocalGroupSubPage,
)
from xr_pages.services import (
    AVAILABLE_PAGE_PERMISSION_TYPES,
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
)


class PagesWebTest(WebTest):
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


class PagesBaseTest(WagtailPageTests):
    def setUp(self):
        site = Site.objects.get()
        self.home_page = site.root_page
        self.root_page = Page.objects.parent_of(self.home_page).get()

    def assertHasGroupPagePermissions(
        self, group, page, permission_types=None, msg=None
    ):
        if permission_types is None:
            permission_types = []

        for permission_type in permission_types:
            if not GroupPagePermission.objects.filter(
                group=group, page=page, permission_type=permission_type
            ).exists():
                msg = self._formatMessage(
                    msg,
                    'Group "%s" has no "%s" permission for page %s.%s but should.'
                    % (
                        group,
                        permission_type,
                        page._meta.app_label,
                        page._meta.model_name,
                    ),
                )
                raise self.failureException(msg)

        no_permission_types = [
            permission_type
            for permission_type in AVAILABLE_PAGE_PERMISSION_TYPES
            if permission_type not in permission_types
        ]

        for permission_type in no_permission_types:
            if GroupPagePermission.objects.filter(
                group=group, page=page, permission_type=permission_type
            ).exists():
                msg = self._formatMessage(
                    msg,
                    'Group "%s" has "%s" permission for page %s.%s but should not.'
                    % (
                        group,
                        permission_type,
                        page._meta.app_label,
                        page._meta.model_name,
                    ),
                )
                raise self.failureException(msg)


class PagesPageTreeTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self.home_sub_page = HomeSubPage.objects.get()
        self.local_group_list_page = LocalGroupListPage.objects.get()

        self.local_group_page = LocalGroupPage(
            title="Example Group", name="Example Group"
        )
        self.local_group_list_page.add_child(instance=self.local_group_page)

        self.local_group_sub_page = LocalGroupSubPage(title="Example SubPage")
        self.local_group_page.add_child(instance=self.local_group_sub_page)

    def test_page_titles(self):
        self.assertEqual(self.home_page.title, "XR Deutschland")

    def test_initial_pages(self):
        home_page_children = Page.objects.child_of(self.home_page).live().specific()

        self.assertIn(self.home_sub_page, home_page_children)
        self.assertIn(self.local_group_list_page, home_page_children)

        local_group_list_page_children = LocalGroupPage.objects.child_of(
            self.local_group_list_page
        ).live()

        self.assertEqual([self.local_group_page], list(local_group_list_page_children))

        local_group_page_children = LocalGroupSubPage.objects.child_of(
            self.local_group_page
        ).live()

        self.assertEqual([self.local_group_sub_page], list(local_group_page_children))

    def test_can_create_pages_under_home_page(self):
        self.assertCanCreateAt(HomePage, HomeSubPage)
        self.assertCanNotCreateAt(HomePage, LocalGroupListPage)
        self.assertCanNotCreateAt(HomePage, LocalGroupPage)
        self.assertCanNotCreateAt(HomePage, LocalGroupSubPage)

    def test_can_create_pages_under_home_sub_page(self):
        self.assertCanNotCreateAt(HomeSubPage, HomePage)
        self.assertCanNotCreateAt(HomeSubPage, LocalGroupListPage)
        self.assertCanNotCreateAt(HomeSubPage, LocalGroupPage)
        self.assertCanNotCreateAt(HomeSubPage, LocalGroupSubPage)

    def test_can_create_pages_under_local_group_list_page(self):
        self.assertCanNotCreateAt(LocalGroupListPage, HomePage)
        self.assertCanNotCreateAt(LocalGroupListPage, HomeSubPage)
        self.assertCanCreateAt(LocalGroupListPage, LocalGroupPage)
        self.assertCanNotCreateAt(LocalGroupListPage, LocalGroupSubPage)

    def test_can_create_pages_under_local_group_page(self):
        self.assertCanNotCreateAt(LocalGroupPage, HomePage)
        self.assertCanNotCreateAt(LocalGroupPage, HomeSubPage)
        self.assertCanNotCreateAt(LocalGroupPage, LocalGroupListPage)
        self.assertCanCreateAt(LocalGroupPage, LocalGroupSubPage)

    def test_can_create_pages_under_local_group_sub_page(self):
        self.assertCanNotCreateAt(LocalGroupSubPage, HomePage)
        self.assertCanNotCreateAt(LocalGroupSubPage, HomeSubPage)
        self.assertCanNotCreateAt(LocalGroupSubPage, LocalGroupListPage)
        self.assertCanNotCreateAt(LocalGroupSubPage, LocalGroupPage)


class PagesGroupPagePermissionsTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self.home_sub_page = HomeSubPage.objects.get()
        self.local_group_list_page = LocalGroupListPage.objects.get()

        self.local_group_page = LocalGroupPage(
            title="Example Group", name="Example Group"
        )
        self.local_group_list_page.add_child(instance=self.local_group_page)

        self.local_group_sub_page = LocalGroupSubPage(title="Example SubPage")
        self.local_group_list_page.add_child(instance=self.local_group_sub_page)

    def test_overall_site_group_page_permissions(self):
        overall_site_moderators = Group.objects.get(name="Overall Site Moderators")
        overall_site_editors = Group.objects.get(name="Overall Site Editors")

        # we only need to check root_page permissions since
        # all other pages inherit the permissions from root_page

        # root_page

        self.assertHasGroupPagePermissions(
            overall_site_moderators,
            self.root_page,
            MODERATORS_PAGE_PERMISSIONS + ["lock"],
        )
        self.assertHasGroupPagePermissions(
            overall_site_editors, self.root_page, EDITORS_PAGE_PERMISSIONS
        )

    def test_regional_group_page_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")

        # root_page

        self.assertHasGroupPagePermissions(regional_moderators, self.root_page, None)
        self.assertHasGroupPagePermissions(regional_editors, self.root_page, None)

        # home_page

        self.assertHasGroupPagePermissions(regional_moderators, self.home_page, None)
        self.assertHasGroupPagePermissions(regional_editors, self.home_page, None)

        # home_sub_page

        self.assertHasGroupPagePermissions(
            regional_moderators, self.home_sub_page, MODERATORS_PAGE_PERMISSIONS
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.home_sub_page, EDITORS_PAGE_PERMISSIONS
        )

        # local_group_list_page

        self.assertHasGroupPagePermissions(
            regional_moderators, self.local_group_list_page, None
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.local_group_list_page, None
        )

        # local_group_page

        self.assertHasGroupPagePermissions(
            regional_moderators, self.local_group_list_page, None
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.local_group_list_page, None
        )

        # local_group_sub_page

        self.assertHasGroupPagePermissions(
            regional_moderators, self.local_group_sub_page, None
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.local_group_sub_page, None
        )

    def test_local_group_page_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")

        # root_page

        self.assertHasGroupPagePermissions(local_moderators, self.root_page, None)
        self.assertHasGroupPagePermissions(local_editors, self.root_page, None)

        # home_page

        self.assertHasGroupPagePermissions(local_moderators, self.home_page, None)
        self.assertHasGroupPagePermissions(local_editors, self.home_page, None)

        # home_sub_page

        self.assertHasGroupPagePermissions(local_moderators, self.home_sub_page, None)
        self.assertHasGroupPagePermissions(local_editors, self.home_sub_page, None)

        # local_group_list_page

        self.assertHasGroupPagePermissions(
            local_moderators, self.local_group_list_page, None
        )
        self.assertHasGroupPagePermissions(
            local_editors, self.local_group_list_page, None
        )

        # local_group_page

        self.assertHasGroupPagePermissions(
            local_moderators, self.local_group_page, MODERATORS_PAGE_PERMISSIONS
        )
        self.assertHasGroupPagePermissions(
            local_editors, self.local_group_page, EDITORS_PAGE_PERMISSIONS
        )

        # local_group_sub_page

        # we do not need to check since local_group_sub_page inherits
        # the permissions from local_group_page
