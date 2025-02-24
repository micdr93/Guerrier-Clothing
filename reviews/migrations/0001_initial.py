# Generated by Django 4.2.18 on 2025-02-24 22:13

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0006_alter_review_options_category_description_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('review', models.TextField(max_length=1500)),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1, 'Rating must be at least 1'), django.core.validators.MaxValueValidator(5, 'Rating cannot exceed 5')])),
                ('verified_purchase', models.BooleanField(default=False)),
                ('helpful_votes', models.PositiveIntegerField(default=0)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews_new', to='products.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_reviews_new', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Reviews',
                'ordering': ['-created_on'],
            },
        ),
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('user', 'product'), name='unique_review_per_user_new'),
        ),
    ]
