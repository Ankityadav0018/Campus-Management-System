from django.db import models
from django.core.cache import cache

class FoodStall(models.Model):
    """Food stall/vendor shop"""
    name = models.CharField(max_length=100, db_index=True)  # Index for name searches
    description = models.TextField(blank=True, null=True)
    vendor = models.ForeignKey('users.User', on_delete=models.CASCADE, limit_choices_to={'role': 'vendor'}, related_name='food_stalls')
    email = models.EmailField(max_length=255, blank=True, null=True, help_text="Stall email address for order notifications")
    contact_phone = models.CharField(max_length=15, blank=True, null=True, help_text="Contact phone number")
    is_active = models.BooleanField(default=True, db_index=True)  # Index for filtering active stalls
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True, null=True, help_text="UPI QR Code for payments")
    upi_id = models.CharField(max_length=100, blank=True, null=True, help_text="UPI ID for generating QR code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.vendor.email}"
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['vendor', 'is_active']),  # Composite index for vendor dashboard
        ]

class FoodItem(models.Model):
    """Food items available at stalls"""
    CATEGORY_CHOICES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snacks', 'Snacks'),
        ('beverages', 'Beverages'),
        ('desserts', 'Desserts'),
    )
    
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE, related_name='food_items', null=True)
    name = models.CharField(max_length=100, db_index=True)  # Index for searches
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='snacks', db_index=True)  # Index for category filtering
    price = models.DecimalField(max_digits=6, decimal_places=2)
    available = models.BooleanField(default=True, db_index=True)  # Index for availability filtering
    image = models.ImageField(upload_to='food_items/', blank=True, null=True)
    preparation_time = models.IntegerField(default=15, help_text="Preparation time in minutes")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.stall.name if self.stall else 'No Stall'}"
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['stall', 'available']),  # Composite index for stall menu queries
            models.Index(fields=['category', 'available']),  # Index for category filtering
        ]

class FoodOrder(models.Model):
    """Customer food orders"""
    student = models.ForeignKey('attendance.Student', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=True, blank=True)
    stall = models.ForeignKey(FoodStall, on_delete=models.CASCADE, related_name='orders', null=True)
    time_slot = models.DateTimeField(auto_now_add=True, db_index=True)  # Index for time-based queries
    pickup_time_slot = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', db_index=True)
    special_instructions = models.TextField(blank=True, null=True)
    PAYMENT_METHOD_CHOICES = (
        ('cod', 'Cash on Delivery'),
        ('qr', 'UPI/QR Code Payment'),
        ('card', 'Debit/Credit Card'),
        ('wallet', 'Campus Wallet'),
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        customer = self.student.name if self.student else (self.user.email if self.user else "Unknown")
        return f'Order #{self.id} by {customer}'
    
    class Meta:
        ordering = ['-time_slot']
        indexes = [
            models.Index(fields=['stall', 'status']),  # Composite index for vendor dashboard
            models.Index(fields=['user', '-time_slot']),  # Index for user order history
            models.Index(fields=['-time_slot', 'status']),  # Index for recent orders by status
        ]

class FoodOrderItem(models.Model):
    """Items in a food order"""
    order = models.ForeignKey(FoodOrder, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=6, decimal_places=2, null=True)

    def __str__(self):
        return f'{self.quantity} x {self.food_item.name}'
    
    def save(self, *args, **kwargs):
        # Store the price at time of order
        if not self.price_at_order:
            self.price_at_order = self.food_item.price
        super().save(*args, **kwargs)
