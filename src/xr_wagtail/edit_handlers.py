from wagtail.admin.edit_handlers import BaseCompositeEditHandler


class FieldCollapsiblePanel(BaseCompositeEditHandler):
    template = "xr_wagtail/edit_handlers/field_collapsible_panel.html"

    def __init__(self, children=(), *args, **kwargs):
        super().__init__(children, *args, **kwargs)
        self.flat_children = []

    def _flatten_children(self, children):
        flat_fields = []
        for child in children:
            if hasattr(child, "children"):
                flat_fields += self._flatten_children(child.children)
            else:
                flat_fields.append(child)
        return flat_fields

    def on_instance_bound(self):
        super().on_instance_bound()
        self.flat_children = self._flatten_children(self.children)
