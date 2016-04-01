# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-23 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timecapture', '0008_auto_20160313_2219'),
    ]

    operations = [
        migrations.AddField(
            model_name='timeuser',
            name='cost_per_hr',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=8, verbose_name='cost per hour'),
        ),
    ]
