# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-25 00:04
from __future__ import unicode_literals

from django.db import migrations, models
import dublyou.utils


class Migration(migrations.Migration):

    dependencies = [
        ('profile', 'rename_profile_model_20170224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='user_image',
            field=models.ImageField(blank=True, null=True, upload_to=dublyou.utils.upload_to_path),
        ),
    ]