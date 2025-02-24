from django.db import migrations

def forward_migrate_reviews(apps, schema_editor):
    # Get the old and new Review models
    OldReview = apps.get_model('products', 'Review')
    NewReview = apps.get_model('reviews', 'Review')
    
    # For each old review, create a new one
    for old_review in OldReview.objects.all():
        NewReview.objects.create(
            product=old_review.product,
            user=old_review.user,
            title=old_review.title,
            review=old_review.review,
            rating=old_review.rating,
            created_on=old_review.created_on,
            updated_on=old_review.updated_on,
            # Set defaults for new fields
            verified_purchase=False,
            helpful_votes=0
        )

def reverse_migrate_reviews(apps, schema_editor):
    # Delete all new reviews (if you need to reverse migration)
    NewReview = apps.get_model('reviews', 'Review')
    NewReview.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('reviews', '0001_initial'),
       
        ('products', '0001_initial'),  
    ]

    operations = [
        migrations.RunPython(forward_migrate_reviews, reverse_migrate_reviews),
    ]