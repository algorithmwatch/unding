# Generated by Django 3.0.10 on 2020-10-21 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0006_auto_20201021_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
