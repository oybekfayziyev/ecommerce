# Generated by Django 3.0.7 on 2020-06-21 12:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='slug',
            field=models.SlugField(default=1),
            preserve_default=False,
        ),
    ]