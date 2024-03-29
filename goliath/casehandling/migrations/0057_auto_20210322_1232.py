# Generated by Django 3.1.5 on 2021-03-22 12:32

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0056_auto_20210315_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='casetype',
            name='max_entity_reminder',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='casetype',
            name='max_user_reminder',
            field=models.DurationField(default=datetime.timedelta(days=7)),
        ),
        migrations.AddField(
            model_name='historicalcasetype',
            name='max_entity_reminder',
            field=models.IntegerField(default=2),
        ),
        migrations.AddField(
            model_name='historicalcasetype',
            name='max_user_reminder',
            field=models.DurationField(default=datetime.timedelta(days=7)),
        ),
    ]
