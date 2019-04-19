from django.contrib.auth.models import Group
from wagtail.core.models import Page
from wagtailmenus.models import MainMenuItem

from xr_events.tests.test_events_pages import EVENT_PAGE_CLASSES
from xr_newsletter.models import NewsletterFormPage, EmailFormPage, NewsletterFormField
from xr_pages.models import HomePage, LocalGroupPage
from xr_pages.services import MODERATORS_PAGE_PERMISSIONS, EDITORS_PAGE_PERMISSIONS
from xr_pages.tests.test_pages import PagesBaseTest, PAGES_PAGE_CLASSES


NEWSLETTER_PAGE_CLASSES = {NewsletterFormPage, EmailFormPage}

NEWSLETTER_BASE_FORM_FIELDS = [
    NewsletterFormField(label="Email", name="email", field_type="email", required=True),
    NewsletterFormField(
        label="Name", name="name", field_type="singleline", required=False
    ),
    NewsletterFormField(
        label="I agree",
        name="gdpr",
        field_type="checkbox",
        required=True,
        help_text=(
            "GDPR Permission: I give my consent to Extinction Rebellion to get "
            "in touch with me using the information I have provided in this "
            "form, for the purpose of news, updates, and rebellion"
        ),
    ),
]


class NewsletterBaseTest(PagesBaseTest):
    def setUp(self):
        super().setUp()

    def _setup_form_pages(self):
        self.newsletter_form_page = NewsletterFormPage.objects.get()
        self.email_form_page = EmailFormPage(
            title="Example Form Page", group=self.local_group
        )
        self.home_page.add_child(instance=self.email_form_page)

        self.FORM_PAGES = {self.newsletter_form_page, self.email_form_page}

        MainMenuItem.objects.get_or_create(
            menu=self.main_menu, link_page=self.newsletter_form_page
        )
        self.newsletter_form_page.show_in_menus = True
        self.newsletter_form_page.save()


class NewsletterPageTreeTest(NewsletterBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_form_pages()

    def test_initial_pages(self):
        home_page_children = Page.objects.child_of(self.home_page).live().specific()

        self.assertIn(self.home_sub_page, home_page_children)

    def test_can_create_newsletter_form_page_under_pages(self):

        self.assertCanCreateAt(LocalGroupPage, NewsletterFormPage)

        for page_class in PAGES_PAGE_CLASSES.union(EVENT_PAGE_CLASSES) - {
            LocalGroupPage
        }:
            self.assertCanNotCreateAt(page_class, NewsletterFormPage)

    def test_can_create_pages_under_newsletter_form_page(self):
        for page_class in PAGES_PAGE_CLASSES.union(EVENT_PAGE_CLASSES):
            self.assertCanNotCreateAt(NewsletterFormPage, page_class)

    def test_can_create_email_form_page_under_pages(self):
        self.assertCanCreateAt(HomePage, EmailFormPage)
        self.assertCanCreateAt(LocalGroupPage, EmailFormPage)

        for page_class in PAGES_PAGE_CLASSES.union(EVENT_PAGE_CLASSES) - {
            LocalGroupPage,
            HomePage,
        }:
            self.assertCanNotCreateAt(page_class, EmailFormPage)

    def test_can_create_pages_under_email_form_page(self):
        for page_class in PAGES_PAGE_CLASSES.union(EVENT_PAGE_CLASSES):
            self.assertCanNotCreateAt(EmailFormPage, page_class)


class NewsletterPagePermissionsTest(NewsletterBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()
        self._setup_form_pages()

    def test_local_group_form_pages_permissions(self):
        local_moderators = Group.objects.get(name="Example Group Page Moderators")
        local_editors = Group.objects.get(name="Example Group Page Editors")

        for page in self.FORM_PAGES:
            for group in [local_moderators, local_editors]:
                self.assertHasGroupPagePermissions(group, page, None)

    def test_regional_group_form_pages_permissions(self):
        regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        regional_editors = Group.objects.get(name="Deutschland Page Editors")

        for group in [regional_moderators, regional_editors]:
            self.assertHasGroupPagePermissions(group, self.email_form_page, None)

        self.assertHasGroupPagePermissions(
            regional_moderators, self.newsletter_form_page, MODERATORS_PAGE_PERMISSIONS
        )
        self.assertHasGroupPagePermissions(
            regional_editors, self.newsletter_form_page, EDITORS_PAGE_PERMISSIONS
        )


class NewsletterSignalsTest(NewsletterBaseTest):
    def setUp(self):
        super().setUp()
        self.regional_moderators = Group.objects.get(name="Deutschland Page Moderators")
        self.regional_editors = Group.objects.get(name="Deutschland Page Editors")

    def test_regional_form_page_create_creates_group_page_permissions(self):
        email_form_page = EmailFormPage(
            title="Special EmailForm", group=self.regional_group
        )
        self.home_page.add_child(instance=email_form_page)

        self.assertHasGroupPagePermissions(
            self.regional_moderators, email_form_page, MODERATORS_PAGE_PERMISSIONS
        )
        self.assertHasGroupPagePermissions(
            self.regional_editors, email_form_page, EDITORS_PAGE_PERMISSIONS
        )

    def test_local_form_page_create_doesnt_create_group_page_permissions(self):
        self._setup_local_group_pages()
        newsletter_form_page = NewsletterFormPage(title="Special NewsletterForm")

        newsletter_form_page.form_fields.set(NEWSLETTER_BASE_FORM_FIELDS)

        self.local_group_page.add_child(instance=newsletter_form_page)

        for group in [self.regional_moderators, self.regional_editors]:
            self.assertHasGroupPagePermissions(group, newsletter_form_page, None)


class NewsletterLocalGroupInheritanceTest(PagesBaseTest):
    def setUp(self):
        super().setUp()
        self._setup_local_group_pages()

    def test_email_form_page_group_get_set(self):
        email_form_page = EmailFormPage(title="Special EmailForm")
        self.local_group_page.add_child(instance=email_form_page)

        self.assertEqual(email_form_page.group.pk, self.local_group_page.group.pk)
        self.assertEqual(email_form_page.group.pk, self.local_group.pk)
