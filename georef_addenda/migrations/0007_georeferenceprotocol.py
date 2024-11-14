# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2024-11-13 15:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('georef_addenda', '0006_auto_20241106_1137'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoreferenceProtocol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Protocol de georeferenciació',
            },
        ),
    ]
