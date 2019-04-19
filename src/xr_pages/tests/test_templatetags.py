from django.template import Context, Template
from django.test import RequestFactory, TestCase

from xr_pages.services import get_site
from ..models import LocalGroupSubPage, LocalGroupPage, LocalGroup


class PagesTemplatetagsTest(TestCase):
    def setUp(self):
        self.site = get_site()
        request_factory = RequestFactory()
        request = request_factory.get("/")
        request.site = self.site
        self.request = request

    def test_get_site(self):
        context = Context({"request": self.request})
        test_template = Template(
            "{% load xr_pages_tags %}" "{% get_site as site %}" "{{ site }}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "localhost [default]")

    def test_get_home_page(self):
        context = Context({"request": self.request})
        test_template = Template(
            "{% load xr_pages_tags %}"
            "{% get_home_page as home_page %}"
            "{{ home_page.title }}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "XR Deutschland")

    def test_get_local_group_list_page(self):
        context = Context({"request": self.request})
        test_template = Template(
            "{% load xr_pages_tags %}"
            "{% get_local_group_list_page as local_group_list_page %}"
            "{{ local_group_list_page.title }}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "Ortsgruppen")

    def test_get_local_groups(self):
        local_group = LocalGroup.objects.create(
            site=self.site, name="LocalGroup SpecialName"
        )
        context = Context({"request": self.request})
        test_template = Template(
            "{% load xr_pages_tags %}"
            "{% get_local_groups as local_groups %}"
            "{% for local_group in local_groups %}{{ local_group.name }}{% endfor %}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "{0}".format(local_group.name))
