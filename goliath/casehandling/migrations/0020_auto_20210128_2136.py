# Generated by Django 3.1.5 on 2021-01-28 21:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('casehandling', '0019_auto_20210119_2233'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='HistoricalReceivedMessage',
            new_name='HistoricalMessageReceived',
        ),
        migrations.RenameModel(
            old_name='HistoricalSentMessage',
            new_name='HistoricalMessageSent',
        ),
        migrations.RenameModel(
            old_name='ReceivedMessage',
            new_name='MessageReceived',
        ),
        migrations.RenameModel(
            old_name='SentMessage',
            new_name='MessageSent',
        ),
        migrations.AlterModelOptions(
            name='historicalmessagereceived',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical message received'},
        ),
        migrations.AlterModelOptions(
            name='historicalmessagesent',
            options={'get_latest_by': 'history_date', 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical message sent'},
        ),
    ]