from django.urls import path
from . import views

app_name = 'food'
urlpatterns = [
    # Customer URLs - Multi-step ordering flow
    path('', views.food_ordering_home, name='food_ordering_home'),
    path('stalls/', views.stall_list, name='stall_list'),
    path('stall/<int:stall_id>/menu/', views.stall_menu, name='stall_menu'),
    path('order/confirm/', views.confirm_order, name='confirm_order'),
    path('order/<int:order_id>/payment/', views.order_payment, name='order_payment'),
    path('order/<int:order_id>/payment/success/', views.payment_success, name='payment_success'),
    path('place-order/', views.place_order, name='place_order'),
    path('place-order/<int:stall_id>/', views.place_order, name='place_order_stall'),
    path('rush-prediction/', views.rush_prediction, name='rush_prediction'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('menu/', views.menu, name='menu'),
    
    # Vendor URLs
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/add-stall/', views.add_stall, name='add_stall'),
    path('vendor/edit-stall/<int:stall_id>/', views.edit_stall, name='edit_stall'),
    path('vendor/delete-stall/<int:stall_id>/', views.delete_stall, name='delete_stall'),
    path('vendor/stall/<int:stall_id>/manage-menu/', views.manage_menu, name='manage_menu'),
    path('vendor/stall/<int:stall_id>/add-item/', views.add_food_item, name='add_food_item'),
    path('vendor/edit-item/<int:item_id>/', views.edit_food_item, name='edit_food_item'),
    path('vendor/delete-item/<int:item_id>/', views.delete_food_item, name='delete_food_item'),
    path('vendor/toggle-item/<int:item_id>/', views.toggle_item_availability, name='toggle_item_availability'),
    path('update-order-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]
