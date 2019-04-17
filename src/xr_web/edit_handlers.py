from wagtail.admin.edit_handlers import BaseCompositeEditHandler


class FieldCollapsiblePanel(BaseCompositeEditHandler):
    template = "xr_web/edit_handlers/field_collapsible_panel.html"
