# Generated by Django 4.0.4 on 2022-05-14 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_groupchatroom_joined_users_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupchatroom',
            name='joined_users_id',
        ),
    ]
