# Generated by Django 3.1.5 on 2021-02-02 16:57

from django.db import migrations, models
import django.db.models.deletion
import markupfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0001_initial'),
        ('casehandling', '0022_auto_20210201_1441'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoliathFlatPage',
            fields=[
                ('flatpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flatpages.flatpage')),
                ('markdown_content', markupfield.fields.MarkupField(blank=True, null=True, rendered_field=True)),
                ('markdown_content_markup_type', models.CharField(choices=[('', '--'), ('html', 'HTML'), ('plain', 'Plain'), ('markdown', 'Markdown')], default='markdown', max_length=30)),
                ('_markdown_content_rendered', models.TextField(editable=False, null=True)),
            ],
            bases=('flatpages.flatpage',),
        ),
    ]