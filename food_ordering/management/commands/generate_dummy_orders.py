from django.core.management.base import BaseCommand
from food_ordering.models import Order, OrderItem, FoodItem
from attendance.models import Student
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generates dummy food orders for rush hour prediction'

    def handle(self, *args, **kwargs):
        students = list(Student.objects.all())
        food_items = list(FoodItem.objects.all())

        if not students:
            self.stdout.write(self.style.ERROR('No students found. Please add some students first.'))
            return
        if not food_items:
            self.stdout.write(self.style.ERROR('No food items found. Please add some food items first.'))
            return

        num_orders = 100 # Generate 100 dummy orders
        start_date = datetime.now() - timedelta(days=30) # Orders from the last 30 days

        for i in range(num_orders):
            random_student = random.choice(students)
            random_hour = random.randint(8, 15) # Orders between 8 AM and 3 PM
            random_minute = random.choice([0, 15, 30, 45])
            random_date = start_date + timedelta(days=random.randint(0, 29))
            order_date = random_date.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)

            pickup_time_slot_choices = [
                '8:00-9:00', '9:00-10:00', '10:00-11:00', '11:00-12:00',
                '12:00-13:00', '13:00-14:00', '14:00-15:00', '15:00-16:00',
            ]
            # Select a pickup time slot that roughly corresponds to the order_date hour
            chosen_pickup_slot = None
            for slot in pickup_time_slot_choices:
                start_hour = int(slot.split('-')[0].split(':')[0])
                end_hour = int(slot.split('-')[1].split(':')[0])
                if start_hour <= random_hour < end_hour:
                    chosen_pickup_slot = slot
                    break
            if not chosen_pickup_slot: # Fallback if no specific slot matches
                chosen_pickup_slot = random.choice(pickup_time_slot_choices)

            order = Order.objects.create(
                student=random_student,
                order_date=order_date,
                pickup_time_slot=chosen_pickup_slot,
                total_price=0, # Will be updated after adding items
                is_paid=True,
            )

            order_total_price = 0
            num_order_items = random.randint(1, 3)
            for _ in range(num_order_items):
                random_food_item = random.choice(food_items)
                quantity = random.randint(1, 3)
                OrderItem.objects.create(
                    order=order,
                    food_item=random_food_item,
                    quantity=quantity
                )
                order_total_price += random_food_item.price * quantity
            
            order.total_price = order_total_price
            order.save()

            self.stdout.write(self.style.SUCCESS(f'Generated order {order.id} for {random_student.name}'))

        self.stdout.write(self.style.SUCCESS('Dummy orders generated successfully!'))
