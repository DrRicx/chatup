# Generated by Django 4.2.13 on 2024-05-15 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0013_favouritemessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
    ]
