# Generated by Django 2.1.7 on 2019-03-24 18:14

from django.db import migrations


def set_localgroup_references(apps, schema_editor):
    LocalGroup = apps.get_model("xr_pages", "LocalGroup")
    LocalGroupPage = apps.get_model("xr_pages", "LocalGroupPage")
    LocalGroupSubPage = apps.get_model("xr_pages", "LocalGroupSubPage")

    for local_group_page in LocalGroupPage.objects.all():
        if local_group_page.is_regional_group:
            group_name = "Deutschland"
        elif local_group_page.name:
            group_name = local_group_page.name
        else:
            raise ValueError(
                "EventGroupPage '%s' has no local_group_page assigned. Please assign "
                "a local_group_page in order to run the migration."
            )

        local_group_qs = LocalGroup.objects.filter(name=group_name)
        if local_group_qs.exists():
            local_group = local_group_qs.get()
        else:
            local_group = LocalGroup.objects.create(
                name=group_name,
                email=local_group_page.email,
                state=local_group_page.state,
                is_regional_group=local_group_page.is_regional_group,
            )

        LocalGroupPage.objects.filter(pk=local_group_page.pk).update(group=local_group)

        # update local_group_page children
        LocalGroupSubPage.objects.filter(path__startswith=local_group_page.path).update(
            group=local_group
        )


class Migration(migrations.Migration):

    dependencies = [("xr_pages", "0024_create_model_localgroup")]

    operations = [
        migrations.RunPython(set_localgroup_references, migrations.RunPython.noop)
    ]