# Generated by Django 3.0.7 on 2020-06-21 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_item_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
    ]