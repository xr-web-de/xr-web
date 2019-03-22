from django.contrib.auth.models import Group
from wagtail.core.models import Page

from xr_pages.models import (
    HomeSubPage,
    LocalGroupListPage,
    LocalGroupPage,
    HomePage,
    LocalGroupSubPage,
)
from xr_pages.services import MODERATORS_PAGE_PERMISSIONS, EDITORS_PAGE_PERMISSIONS
from xr_pages.tests.test_pages import PagesBaseTest, PAGES_PAGE_CLASSES
from xr_events.models import EventListPage, EventGroupPage, EventPage


EVENT_PAGE_CLASSES = {EventListPage, EventGroupPage, EventPage}


class EventsBaseTest(PagesBaseTest):
    def setUp(self):
        super().setUp()

    def _setup_event_pages(self):
        self.event_list_page = EventListPage.objects.get()

        self.regional_event_group_page = EventGroupPage.objects.get()

        self.event_group_page = EventGroupPage(
            title="Example Event Group", local_group=self.local_group_page
        )
        self.event_list_page.add_child(instance=self.event_group_page)

        self.event_page = EventPage(title="Example Event")
        self.event_group_page.add_child(instance=self.event_page)

        self.EVENT_PAGES = {
            self.event_list_page,
            self.event_group_page,
            self.event_page,
        }


class EventsPageTreeTest(EventsBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_event_pages()

    def test_initial_pages(self):
        home_page_children = Page.objects.child_of(self.home_page).live().specific()

        self.assertIn(self.home_sub_page, home_page_children)
        self.assertIn(self.event_list_page, home_page_children)

        event_list_page_children = EventGroupPage.objects.child_of(
            self.event_list_page
        ).live()

        self.assertSetEqual(
            {self.event_group_page, self.regional_event_group_page},
            set(event_list_page_children),
        )

        event_group_page_children = EventPage.objects.child_of(
            self.event_group_page
        ).live()

        self.assertEqual([self.event_page], list(event_group_page_children))

    def test_can_create_pages_under_home_page(self):
        self.assertCanNotCreateAt(HomePage, EventListPage)
        self.assertCanNotCreateAt(HomePage, EventGroupPage)
        self.assertCanNotCreateAt(HomePage, EventPage)

    def test_can_create_pages_under_home_page(self):
        self.assertCanCreateAt(HomePage, HomeSubPage)
        for page_class in EVENT_PAGE_CLASSES:
            self.assertCanNotCreateAt(HomePage, page_class)

    def test_can_create_pages_under_home_sub_page(self):
        for page_class in EVENT_PAGE_CLASSES:
            self.assertCanNotCreateAt(HomeSubPage, page_class)

    def test_can_create_pages_under_local_group_list_page(self):
        for page_class in EVENT_PAGE_CLASSES:
            self.assertCanNotCreateAt(LocalGroupListPage, page_class)

    def test_can_create_pages_under_local_group_page(self):
        for page_class in EVENT_PAGE_CLASSES:
            self.assertCanNotCreateAt(LocalGroupPage, page_class)

    def test_can_create_pages_under_local_group_sub_page(self):
        for page_class in EVENT_PAGE_CLASSES:
            self.assertCanNotCreateAt(LocalGroupSubPage, page_class)

    def test_can_create_pages_under_event_list_page(self):
        self.assertCanCreateAt(EventListPage, EventGroupPage)
        for page_class in EVENT_PAGE_CLASSES.union(PAGES_PAGE_CLASSES) - {
            EventGroupPage
        }:
            self.assertCanNotCreateAt(EventListPage, page_class)

    def test_can_create_pages_under_event_group_page(self):
        self.assertCanCreateAt(EventGroupPage, EventPage)
        for page_class in EVENT_PAGE_CLASSES.union(PAGES_PAGE_CLASSES) - {EventPage}:
            self.assertCanNotCreateAt(EventGroupPage, page_class)

    def test_can_create_pages_under_event_page(self):
        for page_class in EVENT_PAGE_CLASSES.union(PAGES_PAGE_CLASSES):
            self.assertCanNotCreateAt(EventPage, page_class)


class EventsGroupPagePermissionsTest(EventsBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_event_pages()
        self.event_moderators = Group.objects.get(name="Example Group Event Moderators")
        self.event_editors = Group.objects.get(name="Example Group Event Editors")

    def test_event_group_base_page_permissions(self):
        for page in self.BASE_PAGES:
            for group in [self.event_moderators, self.event_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_event_group_event_page_permissions(self):
        # event_list_page

        for group in [self.event_moderators, self.event_editors]:
            self.assertHasGroupPagePermissions(group, self.event_list_page, None)

        # event_group_page

        self.assertHasGroupPagePermissions(
            self.event_moderators, self.event_group_page, MODERATORS_PAGE_PERMISSIONS
        )
        self.assertHasGroupPagePermissions(
            self.event_editors, self.event_group_page, EDITORS_PAGE_PERMISSIONS
        )

        # event_page

        # we do not need to test event_pages, since they inherit from event_group_page

    def test_event_group_local_group_page_permissions(self):
        for page in self.LOCAL_GROUP_PAGES:
            for group in [self.event_moderators, self.event_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_local_group_event_page_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")

        for page in self.EVENT_PAGES:
            for group in [local_moderators, local_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_regional_group_event_page_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")

        for page in self.EVENT_PAGES:
            for group in [regional_moderators, regional_editors]:
                self.assertHasGroupPagePermissions(group, page, None)
