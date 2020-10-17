# Generated by Django 2.2.10 on 2020-10-17 00:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meeting', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='friends_participation',
            field=models.ManyToManyField(related_name='friends_participation', through='meeting.FriendsParticipation', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='room',
            name='meeting',
            field=models.ManyToManyField(related_name='meeting', through='meeting.Meeting', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='meeting',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_room_id', to='meeting.Room'),
        ),
        migrations.AddField(
            model_name='meeting',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meeting_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friendsparticipation',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_room_id', to='meeting.Room'),
        ),
        migrations.AddField(
            model_name='friendsparticipation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='meeting',
            unique_together={('room', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='friendsparticipation',
            unique_together={('room', 'user')},
        ),
    ]
