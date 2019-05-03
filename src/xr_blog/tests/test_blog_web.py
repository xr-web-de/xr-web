from django_webtest import WebTest

from xr_blog.tests.test_blog_pages import BlogBaseTest


class BlogWebTest(BlogBaseTest, WebTest):
    def setUp(self):
        super().setUp()
        self._setup_blog_pages()

    def test_event_list_page(self):
        response = self.app.get(self.blog_list_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.blog_entry_page.title)
        self.assertContains(response, self.blog_list_page.title)

    def test_event_list_page(self):
        response = self.app.get(self.blog_entry_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.blog_entry_page.title)
