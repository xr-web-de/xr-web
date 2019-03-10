from django.db import models, transaction
from wagtail.admin.edit_handlers import StreamFieldPanel, FieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Collection

from .blocks import ContentBlock
from .services import (
    get_or_create_or_update_auth_group_for_page,
    add_group_page_permission,
    get_document_permission,
    add_group_collection_permission,
    get_image_permission,
)


class HomePage(Page):
    template = "xr_pages/pages/home.html"
    content = StreamField(ContentBlock)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []

    is_home_page = True


class StandardPage(Page):
    template = "xr_pages/pages/standard.html"
    content = StreamField(ContentBlock)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = ["HomePage", "LocalGroupPage"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["parent_page"] = self.get_parent()
        return context


class LocalGroupIndexPage(Page):
    template = "xr_pages/pages/local_group_index.html"
    content = StreamField(ContentBlock)

    content_panels = Page.content_panels + [StreamFieldPanel("content")]

    parent_page_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["local_groups"] = (
            LocalGroupPage.objects.child_of(self).live().order_by("-title")
        )
        return context


class LocalGroupPage(Page):
    template = "xr_pages/pages/local_group.html"
    email = models.EmailField(null=True, blank=True)
    content = StreamField(ContentBlock)

    content_panels = Page.content_panels + [
        FieldPanel("email"),
        StreamFieldPanel("content"),
    ]

    parent_page_types = ["LocalGroupIndexPage"]

    is_local_group_page = True

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.id is None

        super().save(*args, **kwargs)

        moderators_group = get_or_create_or_update_auth_group_for_page(
            self, "Moderators"
        )
        editors_group = get_or_create_or_update_auth_group_for_page(self, "Editors")

        # we only need to add permissions on page creation
        if is_new:
            collection = Collection.objects.get(name="Common")

            # Moderators
            for permission_type in ["add", "edit", "publish"]:
                add_group_page_permission(moderators_group, self, permission_type)

            for codename in ["add_document", "change_document", "delete_document"]:
                add_group_collection_permission(
                    moderators_group, collection, get_document_permission(codename)
                )
            for codename in ["add_image", "change_image", "delete_image"]:
                add_group_collection_permission(
                    moderators_group, collection, get_image_permission(codename)
                )

            # Editors
            for permission_type in ["add", "edit"]:
                add_group_page_permission(editors_group, self, permission_type)

            add_group_collection_permission(
                editors_group, collection, get_document_permission("add_document")
            )
            add_group_collection_permission(
                editors_group, collection, get_image_permission("add_image")
            )
