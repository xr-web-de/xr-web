# Generated by Django 2.1.7 on 2019-03-26 00:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("xr_events", "0005_data_set_localgroup_references")]

    operations = [
        migrations.AddField(
            model_name="eventpage",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="eventpage",
            name="start_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
