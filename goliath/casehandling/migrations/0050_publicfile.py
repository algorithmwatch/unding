# Generated by Django 3.1.5 on 2021-03-02 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0049_auto_20210225_1023'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='public_files')),
            ],
        ),
    ]
