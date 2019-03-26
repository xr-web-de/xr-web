from django.template import Context, Template
from django.test import RequestFactory, TestCase
from wagtail.core.models import Site

from ..models import LocalGroupSubPage, LocalGroupPage, LocalGroup


class PagesTemplatetagsTest(TestCase):
    def setUp(self):
        self.site = Site.objects.all().get()
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

    def test_get_local_group_page_for_page(self):
        local_group = LocalGroup.objects.create(name="LocalGroup SpecialName")
        local_group_page = LocalGroupPage(title="SubPageTitle", group=local_group)
        self.site.root_page.add_child(instance=local_group_page)
        context = Context({"request": self.request, "page": local_group_page})
        test_template = Template(
            "{% load xr_pages_tags %}"
            "{% get_local_group_page_for page as local_group_page %}"
            "{{ local_group_page.title }}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "SubPageTitle")

    def test_get_local_group_page_for_subpage(self):
        local_group = LocalGroup.objects.create(name="LocalGroup SpecialName")
        local_group_page = LocalGroupPage(title="SubPageTitle", group=local_group)
        self.site.root_page.add_child(instance=local_group_page)
        local_group_sub_page = LocalGroupSubPage(title="SubPage")
        local_group_page.add_child(instance=local_group_sub_page)
        context = Context({"request": self.request, "page": local_group_sub_page})
        test_template = Template(
            "{% load xr_pages_tags %}"
            "{% get_local_group_page_for page as local_group_page %}"
            "{{ local_group_page.title }}"
        )
        rendered_template = test_template.render(context)
        self.assertEqual(rendered_template, "SubPageTitle")
