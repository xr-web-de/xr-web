# Generated by Django 2.1.7 on 2019-04-19 04:13

from django.db import migrations


def remove_regional_group_page(apps, schema_editor):
    Site = apps.get_model("wagtailcore.Site")
    LocalGroupPage = apps.get_model("xr_pages.LocalGroupPage")
    LocalGroupListPage = apps.get_model("xr_pages.LocalGroupListPage")

    regional_group_page = LocalGroupPage.objects.get(group__is_regional_group=True)
    regional_group_page.delete()

    local_group_list_page = LocalGroupListPage.objects.get()

    local_group_list_page.numchild -= 1
    local_group_list_page.save()


class Migration(migrations.Migration):

    dependencies = [("xr_pages", "0035_localgroup_site")]

    operations = [
        migrations.RunPython(remove_regional_group_page, migrations.RunPython.noop)
    ]
