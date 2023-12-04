# Generated by Django 4.1.13 on 2023-12-04 01:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buildings', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='address',
            field=models.CharField(help_text='Physical address of the building.', max_length=255),
        ),
        migrations.AlterField(
            model_name='building',
            name='audioguides',
            field=models.ManyToManyField(blank=True, help_text='Associated audio guides for the building.', to='buildings.audioguide'),
        ),
        migrations.AlterField(
            model_name='building',
            name='construction_year',
            field=models.IntegerField(help_text='Year when the building was constructed.'),
        ),
        migrations.AlterField(
            model_name='building',
            name='description',
            field=models.TextField(help_text='Detailed description of the building.'),
        ),
        migrations.AlterField(
            model_name='building',
            name='image_urls',
            field=models.JSONField(help_text='JSON-formatted list of URLs to images of the building.'),
        ),
        migrations.AlterField(
            model_name='building',
            name='latitude',
            field=models.FloatField(help_text="Geographic latitude of the building's location."),
        ),
        migrations.AlterField(
            model_name='building',
            name='longitude',
            field=models.FloatField(help_text="Geographic longitude of the building's location."),
        ),
        migrations.AlterField(
            model_name='building',
            name='preview_image_url',
            field=models.CharField(help_text='URL to a preview image of the building.', max_length=1024, validators=[django.core.validators.URLValidator()]),
        ),
        migrations.AlterField(
            model_name='building',
            name='tags',
            field=models.JSONField(help_text='JSON-formatted list of tags related to the building.'),
        ),
        migrations.AlterField(
            model_name='building',
            name='timeline',
            field=models.JSONField(help_text="JSON-formatted data representing key events in the building's history."),
        ),
        migrations.AlterField(
            model_name='building',
            name='type_of_use',
            field=models.CharField(help_text='The intended use of the building (e.g., residential, commercial).', max_length=100),
        ),
    ]
