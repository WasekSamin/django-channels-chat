# Generated by Django 4.0.4 on 2022-05-14 22:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_remove_groupchatroom_joined_users_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='groupchat',
            name='receiver',
        ),
    ]
