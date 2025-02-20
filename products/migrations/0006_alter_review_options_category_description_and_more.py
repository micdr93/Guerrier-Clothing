# Generated by Django 4.2.18 on 2025-02-19 19:32

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0005_rename_reviews_review_remove_review_reviews_per_user_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'ordering': ['-created_on'], 'verbose_name_plural': 'Reviews'},
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='product',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='review',
            name='rating',
            field=models.IntegerField(default=3, validators=[django.core.validators.MinValueValidator(1, 'Rating must be at least 1'), django.core.validators.MaxValueValidator(5, 'Rating cannot exceed 5')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='products.category'),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(default='Default description', max_length=1000),
        ),
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='product_images/'),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(0.01, 'Price must be greater than zero'), django.core.validators.MaxValueValidator(10000, 'Price is too high')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0, 'Rating cannot be negative'), django.core.validators.MaxValueValidator(5, 'Rating cannot exceed 5')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='sizes',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.size'),
        ),
        migrations.AlterField(
            model_name='product',
            name='sku',
            field=models.CharField(blank=True, max_length=254, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='products.product'),
        ),
        migrations.AlterField(
            model_name='review',
            name='review',
            field=models.TextField(max_length=1500),
        ),
        migrations.AlterField(
            model_name='review',
            name='title',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='review',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews', to=settings.AUTH_USER_MODEL),
        ),
    ]
