import datetime

from django.contrib.auth.models import Group

from xr_blog.models import BlogListPage, BlogEntryPage
from xr_pages.models import LocalGroupListPage, LocalGroupPage, HomePage
from xr_pages.services import MODERATORS_PAGE_PERMISSIONS, EDITORS_PAGE_PERMISSIONS
from xr_pages.tests.test_pages import PagesBaseTest, PAGES_PAGE_CLASSES


class BlogBaseTest(PagesBaseTest):
    def setUp(self):
        super().setUp()

    def _setup_blog_pages(self):
        # create local_group(and ..._list_page) if needed
        self.local_group_list_page = LocalGroupListPage.objects.get()

        local_group_page_qs = LocalGroupPage.objects.filter(group=self.local_group)
        if local_group_page_qs.exists():
            self.local_group_page = local_group_page_qs.get()

        else:
            self.local_group_page = LocalGroupPage(
                title="Example Group", group=self.local_group
            )
            self.local_group_list_page.add_child(instance=self.local_group_page)

        # local blog
        self.blog_list_page = BlogListPage(
            title="Example Blog List Page", group=self.local_group
        )
        self.local_group_page.add_child(instance=self.blog_list_page)

        self.blog_entry_page = BlogEntryPage(
            title="Example Blog Entry Page",
            group=self.local_group,
            date=datetime.date.today(),
            author="Joe Example",
        )
        self.blog_list_page.add_child(instance=self.blog_entry_page)

        # regional blog
        self.regional_blog_list_page = BlogListPage(
            title="Regional Blog List Page", group=self.regional_group
        )
        self.home_page.add_child(instance=self.regional_blog_list_page)

        self.regional_blog_entry_page = BlogEntryPage(
            title="Regional Blog Entry Page",
            group=self.regional_group,
            date=datetime.date.today(),
            author="Joe Regio Example",
        )
        self.regional_blog_list_page.add_child(instance=self.regional_blog_entry_page)


class BlogPageTreeTest(BlogBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_blog_pages()

    def test_can_create_blog_list_page_under_pages(self):
        self.assertCanCreateAt(HomePage, BlogListPage)
        self.assertCanCreateAt(LocalGroupPage, BlogListPage)

        for page_class in PAGES_PAGE_CLASSES.union({BlogEntryPage}) - {
            HomePage,
            LocalGroupPage,
        }:
            self.assertCanNotCreateAt(page_class, BlogListPage)

    def test_can_create_blog_entry_page_under_pages(self):
        self.assertCanCreateAt(BlogListPage, BlogEntryPage)

        for page_class in PAGES_PAGE_CLASSES.union({BlogEntryPage}):
            self.assertCanNotCreateAt(page_class, BlogEntryPage)


class BlogPagePermissionsTest(BlogBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_blog_pages()

    def test_local_group_local_blog_pages_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")

        for page in [self.blog_list_page, self.blog_entry_page]:
            for group in [local_moderators, local_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_local_group_regional_blog_pages_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")

        for page in [self.regional_blog_list_page, self.regional_blog_entry_page]:
            for group in [local_moderators, local_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_regional_group_local_blog_pages_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")

        for page in [self.blog_list_page, self.blog_entry_page]:
            for group in [regional_moderators, regional_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_regional_group_regional_blog_pages_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")

        for group in [regional_moderators, regional_editors]:
            self.assertHasGroupPagePermissions(
                group, self.regional_blog_entry_page, None
            )

        self.assertHasGroupPagePermissions(
            regional_moderators,
            self.regional_blog_list_page,
            MODERATORS_PAGE_PERMISSIONS,
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.regional_blog_list_page, EDITORS_PAGE_PERMISSIONS
        )
