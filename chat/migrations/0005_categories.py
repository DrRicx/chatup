# Generated by Django 5.0.4 on 2024-05-02 01:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_channels_admins_channels_is_private'),
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=200)),
                ('channel_root', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='chat.channels')),
            ],
        ),
    ]
