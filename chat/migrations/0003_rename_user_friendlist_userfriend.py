# Generated by Django 5.0.4 on 2024-04-29 01:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_alter_account_profile_picture_channels_friendlist_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='friendlist',
            old_name='user',
            new_name='userFriend',
        ),
    ]
