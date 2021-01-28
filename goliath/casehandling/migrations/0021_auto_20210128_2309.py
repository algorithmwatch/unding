# Generated by Django 3.1.5 on 2021-01-28 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0020_auto_20210128_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='status',
            field=models.CharField(choices=[('EE', 'There was error with sending the email'), ('UV', 'Waiting user verification'), ('ES', 'Waiting until email sent'), ('WR', 'Waiting for response'), ('WU', 'Waiting for user input'), ('CN', 'Closed, given up'), ('CP', 'Closed, case resolved'), ('CM', 'Closed, mixed feelings')], max_length=2),
        ),
        migrations.AlterField(
            model_name='historicalcase',
            name='status',
            field=models.CharField(choices=[('EE', 'There was error with sending the email'), ('UV', 'Waiting user verification'), ('ES', 'Waiting until email sent'), ('WR', 'Waiting for response'), ('WU', 'Waiting for user input'), ('CN', 'Closed, given up'), ('CP', 'Closed, case resolved'), ('CM', 'Closed, mixed feelings')], max_length=2),
        ),
    ]