# Generated by Django 3.1.5 on 2021-02-17 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('casehandling', '0035_auto_20210217_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name='casetype',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalcase',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalcasetype',
            name='slug',
            field=models.SlugField(default='', editable=False, max_length=255),
        ),
        migrations.AlterField(
            model_name='case',
            name='is_contactable',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kontaktierbar'),
        ),
        migrations.AlterField(
            model_name='historicalcase',
            name='is_contactable',
            field=models.BooleanField(blank=True, null=True, verbose_name='Kontaktierbar'),
        ),
    ]