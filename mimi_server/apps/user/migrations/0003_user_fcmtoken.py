# Generated by Django 2.2.10 on 2020-11-02 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20201028_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='fcmToken',
            field=models.TextField(null=True, verbose_name='fcmToken'),
        ),
    ]
