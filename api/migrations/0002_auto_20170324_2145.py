# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 21:45
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='csv',
            options={'ordering': ('-uploaded',)},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ('-uploaded',)},
        ),
        migrations.AddField(
            model_name='csv',
            name='charset',
            field=models.CharField(default='utf-8', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='csv',
            name='csv_file',
            field=models.FileField(upload_to='api/csvs/'),
        ),
        migrations.AlterField(
            model_name='csv',
            name='has_header',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='csv',
            name='header',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, size=None),
        ),
        migrations.AlterField(
            model_name='csv',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
