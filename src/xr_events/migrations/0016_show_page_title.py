# Generated by Django 2.1.7 on 2019-05-12 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("xr_events", "0015_add_default_event_image_fields")]

    operations = [
        migrations.AddField(
            model_name="eventgrouppage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="eventlistpage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="eventpage",
            name="show_page_title",
            field=models.BooleanField(default=True),
        ),
    ]
