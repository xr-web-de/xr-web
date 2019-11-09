import datetime

from django.utils.timezone import localtime
from django_webtest import WebTest

from xr_events.models import EventPage, EventDate, EventGroupPage, ShadowEventPage
from xr_events.tests.test_events_pages import EventsBaseTest


class EventPagesWebTest(EventsBaseTest, WebTest):
    def setUp(self):
        super().setUp()
        self._setup_event_pages()

    def test_event_list_page(self):
        response = self.app.get(self.event_list_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.event_page.title)
        self.assertContains(response, self.regional_event_page.title)

    def test_regional_event_group_page(self):
        response = self.app.get(self.regional_event_group_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response, self.event_page.title)
        self.assertContains(response, self.regional_event_page.title)

    def test_event_group_page(self):
        response = self.app.get(self.event_group_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.event_page.title)
        self.assertNotContains(response, self.regional_event_page.title)

    def test_event_page(self):
        response = self.app.get(self.event_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.event_page.title)
        self.assertNotContains(response, self.regional_event_page.title)

    def test_regional_event_page(self):
        response = self.app.get(self.regional_event_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.regional_event_page.title)
        self.assertNotContains(response, self.event_page.title)


class EventFilterWebTest(EventsBaseTest, WebTest):
    """
    Test filter functionality on event_pages, respectively event_dates.
    Date filter tests assume that only dates within the next month are shown by default
    """

    def setUp(self):
        super().setUp()
        self._setup_event_pages()

    def test_filter_previous_events(self):
        previous_event_page = EventPage(title="Previous Event Page")
        previous_event_page.dates.add(
            EventDate(start=localtime() - datetime.timedelta(1))
        )
        self.event_group_page.add_child(instance=previous_event_page)

        response = self.app.get(self.event_list_page.url)

        self.assertContains(response, self.event_page.title)
        self.assertNotContains(response, previous_event_page.title)

    def test_filter_future_events(self):
        future_event_page = EventPage(title="Future Event Page")
        future_event_page.dates.add(
            EventDate(start=localtime() + datetime.timedelta(31))
        )
        self.event_group_page.add_child(instance=future_event_page)

        response = self.app.get(self.event_list_page.url)

        self.assertContains(response, self.event_page.title)
        self.assertNotContains(response, future_event_page.title)

    def test_filter_previous_dates(self):
        self.event_page.dates.create(start=localtime() - datetime.timedelta(1))
        self.event_page.save()

        response = self.app.get(self.event_list_page.url)

        dates = self.event_page.dates.order_by("start")

        self.assertNotContains(response, "event_date-id-{}".format(dates[0].id))
        self.assertContains(response, "event_date-id-{}".format(dates[1].id))

    def test_filter_future_dates(self):
        self.event_page.dates.create(start=localtime() + datetime.timedelta(31))
        self.event_page.save()

        response = self.app.get(self.event_list_page.url)

        dates = self.event_page.dates.order_by("start")

        self.assertContains(response, "event_date-id-{}".format(dates[0].id))
        self.assertNotContains(response, "event_date-id-{}".format(dates[1].id))

    def test_filter_shows_multiple_dates(self):
        self.event_page.dates.create(start=localtime() + datetime.timedelta(2))
        self.event_page.save()

        response = self.app.get(self.event_list_page.url)

        dates = self.event_page.dates.order_by("start")

        self.assertContains(response, "event_date-id-{}".format(dates[0].id))
        self.assertContains(response, "event_date-id-{}".format(dates[1].id))

    def test_show_previous_month(self):
        response = self.app.get("{}?d=30".format(self.event_list_page.url))
        self.assertContains(
            response, "event_date-id-{}".format(self.event_page.dates.all()[0].id)
        )
        response = self.app.get("{}?d=-30".format(self.event_list_page.url))
        self.assertNotContains(
            response, "event_date-id-{}".format(self.event_page.dates.all()[0].id)
        )


class ShadowEventsWebTest(EventsBaseTest, WebTest):
    """
    Tests the possibility to list events from other local_groups on the own
    event_group_page.
    """

    def setUp(self):
        super().setUp()
        self._setup_event_pages()

    def test_shadow_event_lists_original_event(self):
        other_local_group_name = "Other Test Group"
        other_local_group = self._create_local_group(other_local_group_name)

        other_event_group_page = EventGroupPage(
            title="Other Event Group", group=other_local_group
        )
        self.event_list_page.add_child(instance=other_event_group_page)

        shadow_event_page = ShadowEventPage(
            title="ShadowEvent Page", original_event=self.event_page
        )
        other_event_group_page.add_child(instance=shadow_event_page)

        response = self.app.get(other_event_group_page.url)

        self.assertContains(response, self.event_page.title)
        self.assertContains(
            response, "event_date-id-{}".format(self.event_page.dates.all()[0].id)
        )

    def test_shadow_event_filter_by_days(self):
        other_local_group_name = "Other Test Group"
        other_local_group = self._create_local_group(other_local_group_name)

        other_event_group_page = EventGroupPage(
            title="Other Event Group", group=other_local_group
        )
        self.event_list_page.add_child(instance=other_event_group_page)

        shadow_event_page = ShadowEventPage(
            title="ShadowEvent Page", original_event=self.event_page
        )
        other_event_group_page.add_child(instance=shadow_event_page)

        response = self.app.get("{}?d=-30".format(other_event_group_page.url))

        self.assertNotContains(response, self.event_page.title)
        self.assertNotContains(
            response, "event_date-id-{}".format(self.event_page.dates.all()[0].id)
        )
