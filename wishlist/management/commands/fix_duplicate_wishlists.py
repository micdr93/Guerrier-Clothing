from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from wishlist.models import Wishlist, WishlistItem

class Command(BaseCommand):
    help = 'Fix duplicate wishlists for users'

    def handle(self, *args, **options):
        fixed_count = 0
        
        for user in User.objects.all():
            wishlists = Wishlist.objects.filter(user=user)
            if wishlists.count() > 1:
                # Keep the first wishlist and delete others
                primary_wishlist = wishlists.first()
                self.stdout.write(f"User {user.username} has {wishlists.count()} wishlists. Keeping ID {primary_wishlist.id}.")
                
                for other_wishlist in wishlists.exclude(id=primary_wishlist.id):
                    # Move all items from other wishlist to primary
                    item_count = 0
                    for item in other_wishlist.items.all():
                        # Use get_or_create to avoid duplicates
                        item_obj, created = WishlistItem.objects.get_or_create(
                            wishlist=primary_wishlist,
                            product=item.product,
                            defaults={
                                'notes': item.notes,
                                'priority': item.priority
                            }
                        )
                        if created:
                            item_count += 1
                    
                    self.stdout.write(f"  - Moved {item_count} items from wishlist ID {other_wishlist.id}")
                    # Delete the duplicate wishlist
                    other_wishlist.delete()
                    self.stdout.write(f"  - Deleted wishlist ID {other_wishlist.id}")
                
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(f"Consolidated wishlists for {user.username}"))
        
        if fixed_count == 0:
            self.stdout.write(self.style.SUCCESS("No users with duplicate wishlists found."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Fixed {fixed_count} users with duplicate wishlists"))