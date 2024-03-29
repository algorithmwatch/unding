# Generated by Django 3.0.10 on 2020-10-26 16:36

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0008_auto_20201026_1629'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='receivedmessage',
            options={'ordering': ['sent_at']},
        ),
        migrations.AlterModelOptions(
            name='sentmessage',
            options={'ordering': ['sent_at']},
        ),
        migrations.AlterField(
            model_name='receivedmessage',
            name='cc_addresses',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='receivedmessage',
            name='from_display_name',
            field=models.TextField(blank=True, null=True),
        ),
    ]
