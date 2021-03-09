# Generated by Django 3.1.5 on 2021-03-09 21:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0052_historicalgoliathflatpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceivedAttachments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='private_attachments')),
                ('filename', models.TextField(blank=True, null=True)),
                ('content_type', models.TextField(blank=True, null=True)),
                ('content_disposition', models.CharField(blank=True, max_length=20, null=True)),
                ('message', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='casehandling.receivedmessage')),
            ],
        ),
    ]