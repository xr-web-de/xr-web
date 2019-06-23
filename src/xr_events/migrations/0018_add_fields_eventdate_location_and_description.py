# Generated by Django 2.2.2 on 2019-06-22 13:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("xr_events", "0017_data_add_missing_colors")]

    operations = [
        migrations.AlterModelOptions(
            name="eventdate",
            options={
                "ordering": ["sort_order"],
                "verbose_name": "Termin",
                "verbose_name_plural": "Termine",
            },
        ),
        migrations.AlterModelOptions(
            name="eventorganiser",
            options={
                "ordering": ["sort_order"],
                "verbose_name": "Veranstalter",
                "verbose_name_plural": "Veranstalter",
            },
        ),
        migrations.AddField(
            model_name="eventdate",
            name="description",
            field=models.CharField(
                blank=True,
                help_text="Optional date description. Visible on event detail page only.",
                max_length=1000,
            ),
        ),
        migrations.AddField(
            model_name="eventdate",
            name="location",
            field=models.CharField(
                blank=True,
                help_text="A more specific location, overwrites the events default location.",
                max_length=255,
            ),
        ),
    ]