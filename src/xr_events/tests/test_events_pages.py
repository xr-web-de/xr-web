import datetime

from django.contrib.auth.models import Group
from django.utils import timezone
from wagtail.core.models import Page, Collection
from wagtailmenus.models import MainMenuItem

from xr_events.signals import EVENT_AUTH_GROUP_TYPES
from xr_pages.models import (
    HomeSubPage,
    LocalGroupListPage,
    LocalGroupPage,
    HomePage,
    LocalGroupSubPage,
)
from xr_pages.services import (
    MODERATORS_PAGE_PERMISSIONS,
    EDITORS_PAGE_PERMISSIONS,
    COMMON_COLLECTION_NAME,
    MODERATORS_COLLECTION_PERMISSIONS,
    EDITORS_COLLECTION_PERMISSIONS,
)
from xr_pages.tests.test_pages import PagesBaseTest, PAGES_PAGE_CLASSES
from xr_events.models import EventListPage, EventGroupPage, EventPage, EventDate

EVENT_PAGE_CLASSES = {EventListPage, EventGroupPage, EventPage}


class EventsBaseTest(PagesBaseTest):
    def setUp(self):
        super().setUp()

    def _setup_event_pages(self):
        # create local_group if needed
        self.local_group_list_page = LocalGroupListPage.objects.get()

        local_group_page_qs = LocalGroupPage.objects.filter(group=self.local_group)
        if local_group_page_qs.exists():
            self.local_group_page = local_group_page_qs.get()

        else:
            self.local_group_page = LocalGroupPage(
                title="Example Group", group=self.local_group
            )
            self.local_group_list_page.add_child(instance=self.local_group_page)

        # create event pages
        self.event_list_page = EventListPage.objects.get()

        self.regional_event_group_page = EventGroupPage.objects.get(
            group__is_regional_group=True
        )

        self.regional_event_page = EventPage(title="Example Regional Event Page")
        self.regional_event_page.dates.add(
            EventDate(start=datetime.date.today() + datetime.timedelta(1))
        )
        self.regional_event_group_page.add_child(instance=self.regional_event_page)
        self.regional_event_page.save()

        self.event_group_page = EventGroupPage(
            title="Example Event Group", group=self.local_group
        )
        self.event_list_page.add_child(instance=self.event_group_page)

        self.event_page = EventPage(title="Example Event Page")
        self.event_page.dates.add(
            EventDate(start=datetime.date.today() + datetime.timedelta(1))
        )
        self.event_group_page.add_child(instance=self.event_page)

        self.EVENT_PAGES = {
            self.event_list_page,
            self.event_group_page,
            self.event_page,
            self.regional_event_group_page,
        }

        MainMenuItem.objects.get_or_create(
            menu=self.main_menu, link_page=self.event_list_page
        )
        self.event_list_page.show_in_menus = True
        self.event_list_page.save()


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
        self.assertEqual(self.event_page.group.pk, self.local_group.pk)

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


class EventsGroupCollectionPermissionsTest(EventsBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_event_pages()
        self.event_moderators = Group.objects.get(name="Example Group Event Moderators")
        self.event_editors = Group.objects.get(name="Example Group Event Editors")

    def test_event_group_collection_permissions(self):
        collection = Collection.objects.get(name=COMMON_COLLECTION_NAME)

        self.assertHasGroupCollectionPermissions(
            self.event_moderators, collection, MODERATORS_COLLECTION_PERMISSIONS
        )
        self.assertHasGroupCollectionPermissions(
            self.event_editors, collection, EDITORS_COLLECTION_PERMISSIONS
        )


class EventsSignalsTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self.event_list_page = EventListPage.objects.get()
        self.special_group_name = "Special Group"

    def test_event_group_create_doesnt_create_auth_groups(self):
        self.assertAuthGroupsNotExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

        special_group = self._create_local_group(name=self.special_group_name)

        self.assertAuthGroupsNotExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

    def test_event_group_page_create_creates_event_auth_groups(self):
        special_group = self._create_local_group(name=self.special_group_name)

        self.assertAuthGroupsNotExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

        special_group_page = LocalGroupPage(
            title=self.special_group_name, group=special_group
        )
        self.event_list_page.add_child(instance=special_group_page)

        self.assertAuthGroupsExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

    def test_event_group_page_delete(self):
        special_group = self._create_local_group(name=self.special_group_name)

        special_group_page = LocalGroupPage(
            title=self.special_group_name, group=special_group
        )
        self.event_list_page.add_child(instance=special_group_page)

        self.assertAuthGroupsExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

        special_group_page.delete()

        self.assertAuthGroupsNotExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

    def test_event_group_name_change(self):
        special_group = self._create_local_group(name=self.special_group_name)

        special_group_page = LocalGroupPage(
            title=self.special_group_name, group=special_group
        )
        self.event_list_page.add_child(instance=special_group_page)

        self.assertAuthGroupsExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)

        special_group.name = "Another Group"
        special_group.save()

        self.assertAuthGroupsNotExists(self.special_group_name, EVENT_AUTH_GROUP_TYPES)
        self.assertAuthGroupsExists("Another Group", EVENT_AUTH_GROUP_TYPES)


class EventsEventPageTest(EventsBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_event_pages()

    def test_event_dates_get_set(self):
        date = timezone.now() + datetime.timedelta(1)
        self.event_page.dates.set([EventDate(start=date)])

        self.event_page.save()

        self.assertTrue(self.event_page.dates.exists())
        self.assertEqual(self.event_page.start_date, date)
        self.assertEqual(self.event_page.end_date, date)

    def test_event_dates_get_ordered(self):
        date = timezone.now() + datetime.timedelta(1)
        self.event_page.dates.set([EventDate(start=date)])

        date2 = timezone.now() + datetime.timedelta(1)
        event_date2 = EventDate.objects.create(event_page=self.event_page, start=date2)
        self.event_page.dates.add(event_date2)

        self.event_page.save()

        self.assertTrue(self.event_page.dates.exists())
        self.assertEqual(self.event_page.start_date, date)
        self.assertEqual(self.event_page.end_date, date2)

    def test_event_page_group_get_set(self):
        event_page = LocalGroupSubPage(title="Special EventPage")
        self.event_group_page.add_child(instance=event_page)

        self.assertEqual(event_page.group.pk, self.event_group_page.group.pk)
        self.assertEqual(event_page.group.pk, self.local_group.pk)
