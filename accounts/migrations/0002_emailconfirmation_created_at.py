# Generated by Django 5.1.3 on 2025-02-07 09:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailconfirmation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2025, 2, 7, 10, 0)),
            preserve_default=False,
        ),
    ]
