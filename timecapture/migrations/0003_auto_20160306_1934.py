# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-06 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timecapture', '0002_auto_20160306_1931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timeuser',
            name='date_of_birth',
            field=models.DateTimeField(blank=True, verbose_name='date of birth'),
        ),
    ]
