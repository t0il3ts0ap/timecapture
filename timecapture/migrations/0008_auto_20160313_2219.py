# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-13 22:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('timecapture', '0007_timeuser_is_staff'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timeuser',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
