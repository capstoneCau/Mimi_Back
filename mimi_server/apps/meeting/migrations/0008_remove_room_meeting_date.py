# Generated by Django 2.2.10 on 2020-10-13 02:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0007_auto_20201012_2301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='meeting_date',
        ),
    ]
