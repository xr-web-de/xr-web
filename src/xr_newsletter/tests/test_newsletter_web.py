from unittest import mock

from django.core import mail
from django_webtest import WebTest
from wagtailmenus.models import MainMenuItem

import xr_newsletter
from xr_newsletter.models import NewsletterFormPage
from xr_pages.tests.test_pages import PagesBaseTest


class NewsletterWebTest(PagesBaseTest, WebTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self.newsletter_page = NewsletterFormPage.objects.get(group=self.regional_group)

        self.newsletter_page.sendy_list_id = "sendy_TEST_list_id"
        self.newsletter_page.to_address = "admin@example.com"
        self.newsletter_page.subject = "TEST Subject"
        self.newsletter_page.show_in_menus = True
        self.newsletter_page.save()

        MainMenuItem.objects.get_or_create(
            menu=self.main_menu, link_page=self.newsletter_page
        )

    def test_newsletter_form_page_responds(self):
        response = self.app.get(self.newsletter_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertLinkExists(response, self.home_page)
        self.assertLinkExists(response, self.home_sub_page)
        self.assertLinkExists(response, self.newsletter_page)

    def _populate_newsletter_form(self, form):
        form["email"] = "bob@example.com"
        form["name"] = "Bob"
        form["gdpr"] = True
        return form

    def test_newsletter_form_page_submit(self):
        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscriber_count", return_value=10
        ) as mock_sendy_subscribe:
            self.newsletter_page.sendy_list_id = "sendy_TEST_list_id"
            self.newsletter_page.to_address = "admin@example.com"
            self.newsletter_page.save()

        page = self.app.get(self.newsletter_page.url)
        form = page.forms["newsletter_form"]

        self.assertContains(page, 'id="newsletter_form"')
        self.assertEqual(form.action, self.newsletter_page.url)

        form = self._populate_newsletter_form(form)

        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscribe", return_value="true"
        ) as mock_sendy_subscribe:
            response = form.submit()

            self.assertRedirects(response, self.home_page.get_url())
            response = response.follow()

            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "error")
            # response.mustcontain("success")

            mock_sendy_subscribe.assert_called_once_with(
                "sendy_TEST_list_id", email="bob@example.com", name="Bob", gdpr=True
            )
            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].subject, "TEST Subject")

    def test_newsletter_form_unexpected_api_response(self):
        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscriber_count", return_value=10
        ):
            self.newsletter_page.sendy_list_id = "sendy_TEST_list_id"
            self.newsletter_page.to_address = "admin@example.com"
            self.newsletter_page.save()

        page = self.app.get(self.newsletter_page.url)
        form = page.forms["newsletter_form"]

        self.assertContains(page, 'id="newsletter_form"')
        self.assertEqual(form.action, self.newsletter_page.url)

        form = self._populate_newsletter_form(form)

        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscribe", return_value=b"\nunexpected"
        ):
            response = form.submit()

            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "error")
            # TODO: test error message

    def test_newsletter_form_missing_to_address(self):
        self.newsletter_page.to_address = ""
        self.newsletter_page.save()

        page = self.app.get(self.newsletter_page.url)
        form = page.forms["newsletter_form"]

        self.assertContains(page, 'id="newsletter_form"')
        self.assertEqual(form.action, self.newsletter_page.url)

        form = self._populate_newsletter_form(form)

        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscribe", return_value="true"
        ) as mock_sendy_subscribe:
            response = form.submit()

            self.assertRedirects(response, self.home_page.get_url())
            response = response.follow()

            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "error")
            # response.mustcontain("success")

            mock_sendy_subscribe.assert_called_once_with(
                "sendy_TEST_list_id", email="bob@example.com", name="Bob", gdpr=True
            )
            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 0)

    def test_newsletter_form_missing_sendy_list_id(self):
        self.newsletter_page.sendy_list_id = ""
        self.newsletter_page.save()

        page = self.app.get(self.newsletter_page.url)
        form = page.forms["newsletter_form"]

        self.assertContains(page, 'id="newsletter_form"')
        self.assertEqual(form.action, self.newsletter_page.url)

        form = self._populate_newsletter_form(form)

        with mock.patch.object(
            xr_newsletter.services.sendy_api, "subscribe", return_value="true"
        ) as mock_sendy_subscribe:
            response = form.submit()

            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, "error")
            # response.mustcontain("success")

            mock_sendy_subscribe.assert_not_called()
            # Test that one message has been sent.
            self.assertEqual(len(mail.outbox), 1)

    def test_newsletter_form_gdpr_required(self):
        page = self.app.get(self.newsletter_page.url)
        form = page.forms["newsletter_form"]

        form = self._populate_newsletter_form(form)
        form["gdpr"] = False
        response = form.submit()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")
        self.assertNotContains(response, "success")
