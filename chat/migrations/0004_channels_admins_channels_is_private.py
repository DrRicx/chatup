# Generated by Django 5.0.4 on 2024-05-02 00:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_rename_user_friendlist_userfriend'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='channels',
            name='admins',
            field=models.ManyToManyField(related_name='channel_admins', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='channels',
            name='is_private',
            field=models.BooleanField(default=False),
        ),
    ]
