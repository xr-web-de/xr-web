# Generated by Django 2.1.7 on 2019-05-12 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("xr_pages", "0041_localgrouplistpage_group_null_false")]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="homesubpage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="localgrouplistpage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="localgrouppage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="localgroupsubpage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
    ]
