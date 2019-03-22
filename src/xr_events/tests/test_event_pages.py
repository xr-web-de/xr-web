from wagtail.core.models import Page

from xr_pages.models import (
    HomeSubPage,
    LocalGroupListPage,
    LocalGroupPage,
    HomePage,
    LocalGroupSubPage,
)
from xr_pages.tests.test_pages import PagesBaseTest, PAGES_PAGE_CLASSES
from xr_events.models import EventListPage, EventGroupPage, EventPage


EVENT_PAGE_CLASSES = {EventListPage, EventGroupPage, EventPage}


class EventsPageTreeTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self.home_sub_page = HomeSubPage.objects.get()
        self.local_group_list_page = LocalGroupListPage.objects.get()

        self.local_group_page = LocalGroupPage(
            title="Example Page Group", name="Example page Group"
        )
        self.local_group_list_page.add_child(instance=self.local_group_page)

        self.event_list_page = EventListPage.objects.get()

        self.regional_event_group_page = EventGroupPage.objects.get()

        self.event_group_page = EventGroupPage(
            title="Example Event Group", local_group=self.local_group_page
        )
        self.event_list_page.add_child(instance=self.event_group_page)

        self.event_page = EventPage(title="Example Event")
        self.event_group_page.add_child(instance=self.event_page)

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
