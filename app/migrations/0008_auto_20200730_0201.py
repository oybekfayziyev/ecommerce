# Generated by Django 3.0.8 on 2020-07-29 21:01

import app.utils.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20200730_0056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=app.utils.utils.upload_image_path),
        ),
        migrations.CreateModel(
            name='ItemExtraImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=app.utils.utils.upload_image_path)),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='app.Item')),
            ],
        ),
    ]
