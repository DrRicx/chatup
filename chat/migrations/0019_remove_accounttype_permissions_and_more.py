# Generated by Django 4.2.13 on 2024-05-27 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0018_accounttype_permissions_userpermission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounttype',
            name='permissions',
        ),
        migrations.RemoveField(
            model_name='userpermission',
            name='account_type',
        ),
        migrations.AddField(
            model_name='userpermission',
            name='account_type',
            field=models.ManyToManyField(to='chat.accounttype'),
        ),
    ]
