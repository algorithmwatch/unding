# Generated by Django 3.1.5 on 2021-02-08 18:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0028_auto_20210208_1431'),
    ]

    operations = [
        migrations.RenameField(
            model_name='historicalreceivedmessage',
            old_name='is_autoreplay',
            new_name='is_autoreply',
        ),
        migrations.RenameField(
            model_name='receivedmessage',
            old_name='is_autoreplay',
            new_name='is_autoreply',
        ),
    ]
