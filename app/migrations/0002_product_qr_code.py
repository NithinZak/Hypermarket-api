# Generated by Django 5.0.2 on 2024-02-22 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='qr_code',
            field=models.ImageField(blank=True, null=True, upload_to='product_qrcodes'),
        ),
    ]
