# Generated by Django 4.1.13 on 2024-01-13 16:12

from django.db import migrations, models
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_userprofile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='telephone',
            field=models.CharField(blank=True, default=None, max_length=20, null=True, validators=[users.validators.validate_international_phone_number]),
        ),
    ]
