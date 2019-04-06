from django import template


register = template.Library()


@register.simple_tag()
def get_form_variables_for(form_page=None, id=None):
    form_vars = {}
    if form_page:
        form_vars.update({"form": form_page.get_form(), "action": form_page.get_url()})
    if id:
        form_vars.update({"form_id": "{}_{}".format("email_form_block", id)})

    return form_vars
