from django.shortcuts import render, redirect
from django.contrib import messages
from .models import FoodItem, Order, OrderItem
from .forms import OrderForm, OrderItemForm
from django.forms import inlineformset_factory
from django.db.models.functions import ExtractHour, ExtractWeekDay
from django.utils import timezone

# Define an OrderItemFormSet for handling multiple food items in one order
OrderItemFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1, can_delete=True)

def food_ordering_home(request):
    food_items = FoodItem.objects.filter(available=True)
    return render(request, 'food_ordering/food_ordering_home.html', {'food_items': food_items})

def place_order(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)
            order.total_price = 0  # Initialize total_price
            order.save()

            # Handle order items
            formset = OrderItemFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()
                # Calculate total price based on order items
                for item in order.orderitem_set.all():
                    order.total_price += item.food_item.price * item.quantity
                order.save()
                messages.success(request, 'Your order has been placed successfully!')
                return redirect('food_ordering_home')
            else:
                order.delete() # If order items are invalid, delete the order
                messages.error(request, 'Please correct the errors in the food items.')
        else:
            messages.error(request, 'Please correct the errors in your order details.')
    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()

    food_items = FoodItem.objects.filter(available=True)
    return render(request, 'food_ordering/place_order.html', {
        'order_form': order_form,
        'formset': formset,
        'food_items': food_items,
    })

def rush_prediction(request):
    # Aggregate orders by hour and day of the week to find peak times
    hourly_demand = Order.objects.annotate(hour=ExtractHour('order_date')) \
                               .values('hour') \
                               .annotate(total_orders=Count('id')) \
                               .order_by('-total_orders')

    daily_demand = Order.objects.annotate(weekday=ExtractWeekDay('order_date')) \
                              .values('weekday') \
                              .annotate(total_orders=Count('id')) \
                              .order_by('-total_orders')
    
    # Convert weekday numbers to names for better readability (1=Sunday, 7=Saturday)
    weekday_names = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
        5: 'Thursday', 6: 'Friday', 7: 'Saturday'
    }
    for entry in daily_demand:
        entry['weekday_name'] = weekday_names.get(entry['weekday'], 'Unknown')

    context = {
        'hourly_demand': hourly_demand,
        'daily_demand': daily_demand,
    }
    return render(request, 'food_ordering/rush_prediction.html', context)
