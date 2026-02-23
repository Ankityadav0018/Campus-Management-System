from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import FoodItem, FoodOrder, FoodOrderItem, FoodStall
from .forms import FoodOrderForm, FoodOrderItemForm, FoodStallForm, FoodItemForm
from django.forms import inlineformset_factory
from django.db.models import Count, Sum, Prefetch
from django.db.models.functions import ExtractHour, ExtractWeekDay
from apps.users.decorators import vendor_required
from django.core.cache import cache
from django.http import JsonResponse
from .utils import send_order_receipt_email, send_order_confirmation_to_customer

FoodOrderItemFormSet = inlineformset_factory(FoodOrder, FoodOrderItem, form=FoodOrderItemForm, extra=1, can_delete=True)

@login_required
def food_ordering_home(request):
    """Food ordering home with caching for better performance"""
    cache_key = 'food_ordering_stats'
    context = cache.get(cache_key)
    
    if not context:
        # Use select_related and prefetch_related to optimize queries
        stalls = FoodStall.objects.filter(is_active=True).prefetch_related(
            Prefetch('food_items', queryset=FoodItem.objects.filter(available=True))
        )
        
        total_items = FoodItem.objects.filter(available=True).count()
        total_orders = FoodOrder.objects.count()
        pending_orders = FoodOrder.objects.filter(status='pending').count()
        total_revenue = FoodOrder.objects.aggregate(total=Sum('total_price'))['total'] or 0
        
        context = {
            'stalls': stalls,
            'total_items': total_items,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': round(total_revenue, 2),
        }
        
        # Cache for 5 minutes
        cache.set(cache_key, context, 300)
    
    return render(request, 'food/food_ordering_home.html', context)

@login_required
def stall_list(request):
    """Display list of all active food stalls"""
    stalls = FoodStall.objects.filter(is_active=True).prefetch_related(
        Prefetch('food_items', queryset=FoodItem.objects.filter(available=True))
    ).order_by('name')
    
    context = {'stalls': stalls}
    return render(request, 'food/stall_list.html', context)

@login_required
def stall_menu(request, stall_id):
    """Display menu for a specific stall"""
    stall = get_object_or_404(FoodStall, id=stall_id, is_active=True)
    food_items = FoodItem.objects.filter(stall=stall).order_by('category', 'name')
    
    # Group by category
    items_by_category = {}
    for item in food_items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)
    
    context = {
        'stall': stall,
        'food_items': food_items,
        'items_by_category': items_by_category,
    }
    return render(request, 'food/stall_menu.html', context)

@login_required
def confirm_order(request):
    """Confirm order before payment"""
    if request.method == 'POST':
        # Get order data from session or POST
        order_id = request.session.get('pending_order_id')
        if order_id:
            order = get_object_or_404(FoodOrder, id=order_id, user=request.user)
            return render(request, 'food/confirm_order.html', {'order': order})
    
    messages.error(request, 'No pending order found.')
    return redirect('food:food_ordering_home')

@login_required
def order_payment(request, order_id):
    """Handle order payment"""
    order = get_object_or_404(FoodOrder, id=order_id, user=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cash')
        # In a real application, integrate with payment gateway here
        
        order.status = 'confirmed'
        order.save()
        
        # Clear session
        if 'pending_order_id' in request.session:
            del request.session['pending_order_id']
        
        return redirect('food:payment_success', order_id=order.id)
    
    context = {'order': order}
    return render(request, 'food/order_payment.html', context)

@login_required
def payment_success(request, order_id):
    """Payment success page"""
    order = get_object_or_404(FoodOrder, id=order_id, user=request.user)
    context = {'order': order}
    return render(request, 'food/payment_success.html', context)

@login_required
def place_order(request, stall_id=None):
    """Place a food order - Modern UI with step-by-step process"""
    from apps.attendance.models import Student
    from apps.resources.models import CampusFaculty
    import json
    
    # Get student or faculty profile for current user
    try:
        student = Student.objects.get(email=request.user.email)
    except Student.DoesNotExist:
        student = None
    
    try:
        faculty = CampusFaculty.objects.get(email=request.user.email)
    except CampusFaculty.DoesNotExist:
        faculty = None

    if request.method == 'POST':
        # Check if order data is coming from the new UI (as JSON)
        order_data_json = request.POST.get('order_data')
        
        if order_data_json:
            # New modern UI submission
            try:
                order_data = json.loads(order_data_json)
                
                # Get the stall
                stall = get_object_or_404(FoodStall, id=order_data['stall'], is_active=True)
                
                # Create the order
                order = FoodOrder.objects.create(
                    user=request.user,
                    student=student,
                    stall=stall,
                    pickup_time_slot=order_data['pickup_time_slot'],
                    special_instructions=order_data.get('special_instructions', ''),
                    payment_method=order_data.get('payment_method', 'cod'),
                    payment_status='pending',
                    total_price=0,
                    status='pending'
                )
                
                # Add order items
                total = 0
                for item_data in order_data['items']:
                    food_item = FoodItem.objects.get(id=item_data['food_item'])
                    quantity = int(item_data['quantity'])
                    
                    FoodOrderItem.objects.create(
                        order=order,
                        food_item=food_item,
                        quantity=quantity,
                        price_at_order=food_item.price
                    )
                    
                    total += food_item.price * quantity
                
                # Update total price
                order.total_price = total
                order.save()
                
                # Send email notification to stall
                email_sent = send_order_receipt_email(order)
                if email_sent:
                    messages.info(request, f'📧 Order receipt sent to {order.stall.name}')
                
                # Send confirmation email to customer
                customer_email_sent = send_order_confirmation_to_customer(order)
                if customer_email_sent:
                    messages.info(request, '📧 Order confirmation sent to your email')
                
                # Clear cache
                cache.delete('food_ordering_stats')
                
                messages.success(request, f'✅ Order placed successfully! Order ID: #{order.id} | Total: ₹{order.total_price}')
                return redirect('food:my_orders')
                
            except Exception as e:
                messages.error(request, f'✗ Error placing order: {str(e)}')
                return redirect('food:place_order')
        
        else:
            # Old form-based submission (fallback)
            order_form = FoodOrderForm(request.POST)
            formset = FoodOrderItemFormSet(request.POST)
            
            if order_form.is_valid() and formset.is_valid():
                order = order_form.save(commit=False)
                order.user = request.user
                order.student = student
                order.total_price = 0
                order.save()
                
                formset = FoodOrderItemFormSet(request.POST, instance=order)
                if formset.is_valid():
                    items = formset.save(commit=False)
                    total = 0
                    for item in items:
                        if item.food_item:
                            item.price_at_order = item.food_item.price
                            item.save()
                            total += item.food_item.price * item.quantity
                    
                    order.total_price = total
                    order.save()
                    
                    # Send email notification to stall
                    email_sent = send_order_receipt_email(order)
                    if email_sent:
                        messages.info(request, f'📧 Order receipt sent to {order.stall.name}')
                    
                    # Send confirmation email to customer
                    customer_email_sent = send_order_confirmation_to_customer(order)
                    if customer_email_sent:
                        messages.info(request, '📧 Order confirmation sent to your email')
                    
                    cache.delete('food_ordering_stats')
                    
                    messages.success(request, f'✅ Your order has been placed successfully! Total: ₹{order.total_price}')
                    return redirect('food:my_orders')
                else:
                    order.delete()
                    messages.error(request, '✗ Please select at least one food item with quantity.')
            else:
                if not order_form.is_valid():
                    for field, errors in order_form.errors.items():
                        for error in errors:
                            messages.error(request, f'{field}: {error}')
                if not formset.is_valid():
                    messages.error(request, '✗ Please select at least one food item and specify quantity.')
    
    # GET request - display the ordering page
    stalls = FoodStall.objects.filter(is_active=True).order_by('name')
    
    # Get all available food items with their details
    food_items = FoodItem.objects.filter(available=True).select_related('stall').values(
        'id', 'name', 'description', 'category', 'price', 'stall_id', 'available', 'image'
    )
    
    # Convert QuerySet to list and format for JSON
    food_items_list = []
    for item in food_items:
        food_items_list.append({
            'id': item['id'],
            'name': item['name'],
            'description': item['description'] or '',
            'category': item['category'],
            'price': float(item['price']),
            'stall_id': item['stall_id'],
            'available': item['available'],
            'image': item['image'] if item['image'] else None
        })
    
    context = {
        'stalls': stalls,
        'food_items': json.dumps(food_items_list),
    }
    
    return render(request, 'food/place_order.html', context)

@login_required
def rush_prediction(request):
    """Rush hour prediction with optimized queries"""
    cache_key = 'rush_prediction_data'
    context = cache.get(cache_key)
    
    if not context:
        hourly_demand = FoodOrder.objects.annotate(hour=ExtractHour('time_slot')) \
                                   .values('hour') \
                                   .annotate(total_orders=Count('id')) \
                                   .order_by('-total_orders')[:10]
        
        daily_demand = FoodOrder.objects.annotate(weekday=ExtractWeekDay('time_slot')) \
                                  .values('weekday') \
                                  .annotate(total_orders=Count('id')) \
                                  .order_by('-total_orders')
        
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
        
        # Cache for 30 minutes
        cache.set(cache_key, context, 1800)
    
    return render(request, 'food/rush_prediction.html', context)

@login_required
def my_orders(request):
    """View user's orders - optimized with prefetch"""
    orders = FoodOrder.objects.filter(user=request.user).select_related('stall').prefetch_related(
        Prefetch('items', queryset=FoodOrderItem.objects.select_related('food_item'))
    ).order_by('-time_slot')[:20]
    
    return render(request, 'food/my_orders.html', {'orders': orders})

@login_required
def menu(request):
    """View all food items by stall - optimized"""
    cache_key = 'food_menu_all'
    context = cache.get(cache_key)
    
    if not context:
        stalls = FoodStall.objects.filter(is_active=True).prefetch_related(
            Prefetch('food_items', queryset=FoodItem.objects.select_related('stall'))
        ).order_by('name')
        
        context = {'stalls': stalls}
        
        # Cache for 10 minutes
        cache.set(cache_key, context, 600)
    
    return render(request, 'food/menu.html', context)

@login_required
@vendor_required
def vendor_dashboard(request):
    """Vendor dashboard to manage stalls and orders"""
    vendor_stalls = FoodStall.objects.filter(vendor=request.user).prefetch_related(
        Prefetch('food_items', queryset=FoodItem.objects.all())
    )
    
    # Get all orders for vendor's stalls (don't slice yet)
    vendor_orders_base = FoodOrder.objects.filter(
        stall__vendor=request.user
    ).select_related('stall', 'user').prefetch_related('items')
    
    # Statistics (calculate before slicing)
    total_stalls = vendor_stalls.count()
    total_items = FoodItem.objects.filter(stall__vendor=request.user).count()
    pending_orders_count = vendor_orders_base.filter(status='pending').count()
    total_revenue = vendor_orders_base.filter(status='completed').aggregate(total=Sum('total_price'))['total'] or 0
    
    # Now get recent orders for display (slice at the end)
    vendor_orders = vendor_orders_base.order_by('-time_slot')[:20]
    
    context = {
        'vendor_stalls': vendor_stalls,
        'vendor_orders': vendor_orders,
        'total_stalls': total_stalls,
        'total_items': total_items,
        'pending_orders_count': pending_orders_count,
        'total_revenue': round(total_revenue, 2),
    }
    
    return render(request, 'food/vendor_dashboard.html', context)

@login_required
@vendor_required
def add_stall(request):
    """Add a new food stall"""
    if request.method == 'POST':
        form = FoodStallForm(request.POST)
        if form.is_valid():
            stall = form.save(commit=False)
            stall.vendor = request.user
            stall.save()
            
            # Clear cache
            cache.delete('food_ordering_stats')
            cache.delete('food_menu_all')
            
            messages.success(request, f'Food stall "{stall.name}" created successfully!')
            return redirect('food:vendor_dashboard')
    else:
        form = FoodStallForm()
    
    return render(request, 'food/add_stall.html', {'form': form})

@login_required
@vendor_required
def edit_stall(request, stall_id):
    """Edit food stall"""
    stall = get_object_or_404(FoodStall, id=stall_id, vendor=request.user)
    
    if request.method == 'POST':
        form = FoodStallForm(request.POST, instance=stall)
        if form.is_valid():
            form.save()
            
            # Clear cache
            cache.delete('food_ordering_stats')
            cache.delete('food_menu_all')
            
            messages.success(request, f'Stall "{stall.name}" updated successfully!')
            return redirect('food:vendor_dashboard')
    else:
        form = FoodStallForm(instance=stall)
    
    return render(request, 'food/edit_stall.html', {'form': form, 'stall': stall})

@login_required
@vendor_required
def delete_stall(request, stall_id):
    """Delete food stall"""
    if request.method == 'POST':
        stall = get_object_or_404(FoodStall, id=stall_id, vendor=request.user)
        stall_name = stall.name
        stall.delete()
        
        # Clear cache
        cache.delete('food_ordering_stats')
        cache.delete('food_menu_all')
        
        messages.success(request, f'Stall "{stall_name}" deleted successfully!')
    
    return redirect('food:vendor_dashboard')

@login_required
@vendor_required
def add_food_item(request, stall_id):
    """Add food item to stall"""
    stall = get_object_or_404(FoodStall, id=stall_id, vendor=request.user)
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_item = form.save(commit=False)
            food_item.stall = stall
            food_item.save()
            
            # Clear cache
            cache.delete('food_ordering_stats')
            cache.delete('food_menu_all')
            
            messages.success(request, f'Food item "{food_item.name}" added to {stall.name}!')
            return redirect('food:manage_menu', stall_id=stall.id)
    else:
        form = FoodItemForm()
    
    return render(request, 'food/add_food_item.html', {'form': form, 'stall': stall})

@login_required
@vendor_required
def edit_food_item(request, item_id):
    """Edit food item"""
    food_item = get_object_or_404(FoodItem, id=item_id, stall__vendor=request.user)
    
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food_item)
        if form.is_valid():
            form.save()
            
            # Clear cache
            cache.delete('food_ordering_stats')
            cache.delete('food_menu_all')
            
            messages.success(request, f'Food item "{food_item.name}" updated successfully!')
            return redirect('food:manage_menu', stall_id=food_item.stall.id)
    else:
        form = FoodItemForm(instance=food_item)
    
    return render(request, 'food/edit_food_item.html', {'form': form, 'food_item': food_item})

@login_required
@vendor_required
def delete_food_item(request, item_id):
    """Delete food item"""
    if request.method == 'POST':
        food_item = get_object_or_404(FoodItem, id=item_id, stall__vendor=request.user)
        stall_id = food_item.stall.id
        item_name = food_item.name
        food_item.delete()
        
        # Clear cache
        cache.delete('food_ordering_stats')
        cache.delete('food_menu_all')
        
        messages.success(request, f'Food item "{item_name}" deleted successfully!')
        return redirect('food:manage_menu', stall_id=stall_id)
    
    return redirect('food:vendor_dashboard')

@login_required
@vendor_required
def manage_menu(request, stall_id):
    """Manage food items for a specific stall"""
    stall = get_object_or_404(FoodStall, id=stall_id, vendor=request.user)
    food_items = FoodItem.objects.filter(stall=stall).order_by('category', 'name')
    
    # Group by category
    items_by_category = {}
    for item in food_items:
        if item.category not in items_by_category:
            items_by_category[item.category] = []
        items_by_category[item.category].append(item)
    
    context = {
        'stall': stall,
        'food_items': food_items,
        'items_by_category': items_by_category,
    }
    
    return render(request, 'food/manage_menu.html', context)

@login_required
@vendor_required
def update_order_status(request, order_id):
    """Update order status - only accessible by vendors"""
    if request.method == 'POST':
        order = get_object_or_404(FoodOrder, id=order_id, stall__vendor=request.user)
        new_status = request.POST.get('status')
        
        if new_status in dict(FoodOrder.STATUS_CHOICES):
            order.status = new_status
            order.save()
            
            # Clear cache
            cache.delete('food_ordering_stats')
            
            messages.success(request, f'Order #{order_id} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status')
    
    return redirect('food:vendor_dashboard')

@login_required
@vendor_required
def toggle_item_availability(request, item_id):
    """Quick toggle for food item availability"""
    if request.method == 'POST':
        food_item = get_object_or_404(FoodItem, id=item_id, stall__vendor=request.user)
        food_item.available = not food_item.available
        food_item.save()
        
        # Clear cache
        cache.delete('food_ordering_stats')
        cache.delete('food_menu_all')
        
        status = "available" if food_item.available else "unavailable"
        return JsonResponse({'success': True, 'status': status, 'available': food_item.available})
    
    return JsonResponse({'success': False}, status=400)
