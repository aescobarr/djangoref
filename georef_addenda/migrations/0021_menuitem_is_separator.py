# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2022-08-02 08:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('georef_addenda', '0020_auto_20220802_0744'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='is_separator',
            field=models.BooleanField(default=False),
        ),
    ]
