# Generated by Django 3.1.5 on 2021-02-19 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0036_auto_20210217_1547'),
    ]

    operations = [
        migrations.RenameField(
            model_name='case',
            old_name='last_reminder_sent_at',
            new_name='last_user_reminder_sent_at',
        ),
        migrations.RenameField(
            model_name='case',
            old_name='sent_reminders',
            new_name='sent_user_reminders',
        ),
        migrations.RenameField(
            model_name='historicalcase',
            old_name='last_reminder_sent_at',
            new_name='last_user_reminder_sent_at',
        ),
        migrations.RenameField(
            model_name='historicalcase',
            old_name='sent_reminders',
            new_name='sent_user_reminders',
        ),
    ]
