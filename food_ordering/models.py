from django.db import models

class FoodItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    student = models.ForeignKey('attendance.Student', on_delete=models.CASCADE) # Assuming Student model from attendance app
    order_date = models.DateTimeField(auto_now_add=True)
    pickup_time_slot = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=7, decimal_places=2)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f'Order #{self.id} by {self.student.name}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} x {self.food_item.name}'
