# Generated by Django 2.2.10 on 2020-11-10 02:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0003_auto_20201017_0041'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendsparticipation',
            name='party_number',
            field=models.CharField(default='aa', max_length=30),
            preserve_default=False,
        ),
    ]
