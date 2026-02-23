from django.core.management.base import BaseCommand
from food_ordering.models import FoodItem

class Command(BaseCommand):
    help = 'Adds dummy food items to the database'

    def handle(self, *args, **kwargs):
        food_items_data = [
            {'name': 'Pizza Slice', 'description': 'Delicious cheese pizza slice', 'price': 120.00},
            {'name': 'Burger', 'description': 'Classic beef burger with fries', 'price': 150.00},
            {'name': 'Salad Bowl', 'description': 'Fresh and healthy salad', 'price': 100.00},
            {'name': 'Coffee', 'description': 'Hot brewed coffee', 'price': 60.00},
            {'name': 'Sandwich', 'description': 'Grilled chicken sandwich', 'price': 90.00},
        ]

        for item_data in food_items_data:
            food_item, created = FoodItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'description': item_data['description'],
                    'price': item_data['price']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully added food item: {food_item.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Food item already exists: {food_item.name}'))

        self.stdout.write(self.style.SUCCESS('Dummy food items added successfully!'))
