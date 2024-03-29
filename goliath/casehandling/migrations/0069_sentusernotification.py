# Generated by Django 3.2.11 on 2022-01-27 14:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0068_auto_20211129_1818'),
    ]

    operations = [
        migrations.CreateModel(
            name='SentUserNotification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('from_email', models.EmailField(max_length=254)),
                ('to_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('subject', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('sent_at', models.DateTimeField()),
                ('esp_message_id', models.CharField(max_length=255, null=True)),
                ('esp_message_status', models.CharField(max_length=255, null=True)),
                ('case', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='casehandling.case')),
            ],
            options={
                'ordering': ['sent_at'],
                'abstract': False,
            },
        ),
    ]
