# Generated by Django 3.1.5 on 2021-03-15 16:04

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('casehandling', '0054_auto_20210309_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casetype',
            name='icon_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='casetype',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='externalsupport',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='historicalcasetype',
            name='icon_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
