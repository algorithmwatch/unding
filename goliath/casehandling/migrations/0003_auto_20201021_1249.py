# Generated by Django 3.0.10 on 2020-10-21 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0002_auto_20201021_1248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sentmessage',
            name='esp_message_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='sentmessage',
            name='esp_message_status',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
