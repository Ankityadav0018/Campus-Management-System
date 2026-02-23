from django import forms
from .models import FoodOrder, FoodOrderItem, FoodItem, FoodStall
from apps.attendance.models import Student

class FoodStallForm(forms.ModelForm):
    """Form for vendors to create/edit their food stalls"""
    class Meta:
        model = FoodStall
        fields = ['name', 'description', 'is_active', 'opening_time', 'closing_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter stall name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your food stall'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

class FoodItemForm(forms.ModelForm):
    """Form for vendors to add/edit food items"""
    class Meta:
        model = FoodItem
        fields = ['name', 'description', 'category', 'price', 'available', 'image', 'preparation_time']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief description'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'preparation_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
        }

class FoodOrderForm(forms.ModelForm):
    stall = forms.ModelChoiceField(
        queryset=FoodStall.objects.filter(is_active=True),
        empty_label="Select Food Stall",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
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
        label="Pickup Time Slot",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = FoodOrder
        fields = ['stall', 'pickup_time_slot', 'special_instructions']
        widgets = {
            'special_instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Any special requests?'}),
        }

class FoodOrderItemForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}))

    class Meta:
        model = FoodOrderItem
        fields = ['food_item', 'quantity']
        widgets = {
            'food_item': forms.Select(attrs={'class': 'form-control'}),
        }
