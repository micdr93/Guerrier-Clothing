# Generated by Django 5.1.4 on 2025-01-11 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0002_alter_category_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="description",
            field=models.CharField(default="Default description", max_length=255),
        ),
    ]
