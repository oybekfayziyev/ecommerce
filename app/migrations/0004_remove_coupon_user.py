# Generated by Django 3.0.8 on 2020-07-27 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200727_2310'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='user',
        ),
    ]