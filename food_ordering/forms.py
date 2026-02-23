from django import forms
from .models import Order, OrderItem, FoodItem
from attendance.models import Student

class OrderForm(forms.ModelForm):
    # This form will be used to select the student and pickup time slot
    # Food items will be added separately, possibly via JavaScript or another formset
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select Student")
    pickup_time_slot = forms.ChoiceField(
        choices=[
            ('8:00-9:00', '8:00 AM - 9:00 AM'),
            ('9:00-10:00', '9:00 AM - 10:00 AM'),
            ('10:00-11:00', '10:00 AM - 11:00 AM'),
            ('11:00-12:00', '11:00 AM - 12:00 PM'),
            ('12:00-13:00', '12:00 PM - 1:00 PM'),
            ('13:00-14:00', '1:00 PM - 2:00 PM'),
            ('14:00-15:00', '2:00 PM - 3:00 PM'),
            ('15:00-16:00', '3:00 PM - 4:00 PM'),
        ],
        label="Pickup Time Slot"
    )

    class Meta:
        model = Order
        fields = ['student', 'pickup_time_slot']

class OrderItemForm(forms.ModelForm):
    food_item = forms.ModelChoiceField(queryset=FoodItem.objects.filter(available=True), empty_label="Select Food Item")
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = OrderItem
        fields = ['food_item', 'quantity']
