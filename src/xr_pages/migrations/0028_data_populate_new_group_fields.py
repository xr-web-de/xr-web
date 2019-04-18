# Generated by Django 2.1.7 on 2019-04-05 11:48

from django.db import migrations


def populate_new_group_fields(apps, schema_editor):
    LocalGroup = apps.get_model("xr_pages", "LocalGroup")
    HomePage = apps.get_model("xr_pages", "HomePage")
    HomeSubPage = apps.get_model("xr_pages", "HomeSubPage")

    regional_group = LocalGroup.objects.get(is_regional_group=True)

    homepage = HomePage.objects.get()
    homepage.group = regional_group
    homepage.save()

    for sub_page in HomeSubPage.objects.all():
        sub_page.group = regional_group
        sub_page.save()


class Migration(migrations.Migration):

    dependencies = [("xr_pages", "0027_add_new_group_fields_to_home_pages")]

    operations = [
        migrations.RunPython(populate_new_group_fields, migrations.RunPython.noop)
    ]