from django_webtest import WebTest

from xr_events.tests.test_events_pages import EventsBaseTest


class PagesWebTest(EventsBaseTest, WebTest):
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

    def test_regional_event_page(self):
        response = self.app.get(self.regional_event_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.regional_event_page.title)
