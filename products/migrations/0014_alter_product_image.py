# Generated by Django 4.2.18 on 2025-03-09 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0013_remove_product_updated"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="product_images/"),
        ),
    ]
