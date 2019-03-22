from django.contrib.auth.models import Group
from wagtail.core.models import (
    Site,
    Page,
    GroupPagePermission,
    Collection,
    GroupCollectionPermission,
)
from wagtail.tests.utils import WagtailPageTests

from xr_pages.models import (
    HomePage,
    HomeSubPage,
    LocalGroupListPage,
    LocalGroupPage,
    LocalGroupSubPage,
)
from xr_pages.services import (
    AVAILABLE_PAGE_PERMISSION_TYPES,
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
    MODERATORS_COLLECTION_PERMISSIONS,
    AVAILABLE_COLLECTION_PERMISSION_TYPES,
    EDITORS_COLLECTION_PERMISSIONS,
    COMMON_COLLECTION_NAME,
    get_collection_permission,
)


PAGES_PAGE_CLASSES = {
    HomePage,
    HomeSubPage,
    LocalGroupListPage,
    LocalGroupPage,
    LocalGroupSubPage,
}


class PagesBaseTest(WagtailPageTests):
    def setUp(self):
        site = Site.objects.get()
        self.home_page = site.root_page
        self.root_page = Page.objects.parent_of(self.home_page).get()
        self.home_sub_page = HomeSubPage.objects.get()

        self.BASE_PAGES = {self.home_sub_page, self.root_page, self.home_sub_page}

    def _setup_local_group_pages(self):
        self.local_group_list_page = LocalGroupListPage.objects.get()

        self.local_group_page = LocalGroupPage(
            title="Example Group", name="Example Group"
        )
        self.local_group_list_page.add_child(instance=self.local_group_page)

        self.local_group_sub_page = LocalGroupSubPage(title="Example SubPage")
        self.local_group_page.add_child(instance=self.local_group_sub_page)

        self.LOCAL_GROUP_PAGES = {
            self.local_group_list_page,
            self.local_group_page,
            self.local_group_sub_page,
        }

    def assertHasGroupPagePermissions(
        self, group, page, permission_types=None, msg=None, exact=True
    ):
        if permission_types is None:
            permission_types = []

        for permission_type in AVAILABLE_PAGE_PERMISSION_TYPES:
            has_permission = GroupPagePermission.objects.filter(
                group=group, page=page, permission_type=permission_type
            ).exists()

            should_have_permission = permission_type in permission_types
            if not has_permission and should_have_permission:
                msg = self._formatMessage(
                    msg,
                    'Group "%s" has no "%s" permission for page %s.%s but should.'
                    % (
                        group.name,
                        permission_type,
                        page._meta.app_label,
                        page._meta.model_name,
                    ),
                )
                raise self.failureException(msg)

            elif exact and has_permission and not should_have_permission:
                msg = self._formatMessage(
                    msg,
                    'Group "%s" has "%s" permission for page %s.%s but should not.'
                    % (
                        group.name,
                        permission_type,
                        page._meta.app_label,
                        page._meta.model_name,
                    ),
                )
                raise self.failureException(msg)

    def assertHasGroupCollectionPermissions(
        self, groups, collection, permission_types=None, msg=None, exact=True
    ):
        if permission_types is None:
            permission_types = []

        if not isinstance(groups, (list, tuple, set)):
            groups = [groups]

        for group in groups:
            for permission_type in AVAILABLE_COLLECTION_PERMISSION_TYPES:
                permission = get_collection_permission(permission_type)

                has_permission = GroupCollectionPermission.objects.filter(
                    group=group, collection=collection, permission=permission
                ).exists()

                should_have_permission = permission_type in permission_types

                if not has_permission and should_have_permission:
                    msg = self._formatMessage(
                        msg,
                        'Group "%s" has no "%s" permission for collection "%s" but should.'
                        % (group.name, permission_type, collection.name),
                    )
                    raise self.failureException(msg)

                if exact and has_permission and not should_have_permission:
                    msg = self._formatMessage(
                        msg,
                        'Group "%s" has "%s" permission for collection "%s" but should not.'
                        % (group.name, permission_type, collection.name),
                    )
                    raise self.failureException(msg)


class PagesPageTreeTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()

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
        for page_class in PAGES_PAGE_CLASSES - {HomeSubPage}:
            self.assertCanNotCreateAt(HomePage, page_class)

    def test_can_create_pages_under_home_sub_page(self):
        for page_class in PAGES_PAGE_CLASSES:
            self.assertCanNotCreateAt(HomeSubPage, page_class)

    def test_can_create_pages_under_local_group_list_page(self):
        self.assertCanCreateAt(LocalGroupListPage, LocalGroupPage)
        for page_class in PAGES_PAGE_CLASSES - {LocalGroupPage}:
            self.assertCanNotCreateAt(LocalGroupListPage, page_class)

    def test_can_create_pages_under_local_group_page(self):
        self.assertCanCreateAt(LocalGroupPage, LocalGroupSubPage)
        for page_class in PAGES_PAGE_CLASSES - {LocalGroupSubPage}:
            self.assertCanNotCreateAt(LocalGroupPage, page_class)

    def test_can_create_pages_under_local_group_sub_page(self):
        for page_class in PAGES_PAGE_CLASSES:
            self.assertCanNotCreateAt(LocalGroupSubPage, page_class)


class PagesGroupPagePermissionsTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()

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

    def test_regional_group_base_page_permissions(self):
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

    def test_regional_group_local_group_page_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")
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

    def test_local_group_base_page_permissions(self):
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

    def test_local_group_local_group_page_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")
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

    def test_change_local_group_name_changes_page_group_names(self):
        self.assertTrue(
            Group.objects.filter(name="Example Group Page Moderators").exists()
        )
        self.assertTrue(
            Group.objects.filter(name="Example Group Page Editors").exists()
        )

        self.local_group_page.name = "Another Group"
        self.local_group_page.save()

        self.assertFalse(
            Group.objects.filter(name="Example Group Page Moderators").exists()
        )
        self.assertFalse(
            Group.objects.filter(name="Example Group Page Editors").exists()
        )
        self.assertTrue(
            Group.objects.filter(name="Another Group Page Moderators").exists()
        )
        self.assertTrue(
            Group.objects.filter(name="Another Group Page Editors").exists()
        )


class PagesGroupCollectionPermissionsTest(PagesBaseTest):
    def test_regional_group_collection_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")
        collection = Collection.objects.get(name=COMMON_COLLECTION_NAME)

        self.assertHasGroupCollectionPermissions(
            regional_moderators, collection, MODERATORS_COLLECTION_PERMISSIONS
        )
        self.assertHasGroupCollectionPermissions(
            regional_editors, collection, EDITORS_COLLECTION_PERMISSIONS
        )

    def test_overall_site_collection_permissions(self):
        overall_site_moderators = Group.objects.get(name="Overall Site Moderators")
        overall_site_editors = Group.objects.get(name="Overall Site Editors")
        collection = Collection.objects.get(name="Root")

        self.assertHasGroupCollectionPermissions(
            overall_site_moderators, collection, MODERATORS_COLLECTION_PERMISSIONS
        )
        self.assertHasGroupCollectionPermissions(
            overall_site_editors, collection, EDITORS_COLLECTION_PERMISSIONS
        )

    def test_local_group_collection_permissions(self):
        # create a local group
        local_group_page = LocalGroupPage(title="Example Group", name="Example Group")
        local_group_list_page = LocalGroupListPage.objects.get()
        local_group_list_page.add_child(instance=local_group_page)

        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")
        collection = Collection.objects.get(name=COMMON_COLLECTION_NAME)

        self.assertHasGroupCollectionPermissions(
            local_moderators, collection, MODERATORS_COLLECTION_PERMISSIONS
        )
        self.assertHasGroupCollectionPermissions(
            local_editors, collection, EDITORS_COLLECTION_PERMISSIONS
        )
