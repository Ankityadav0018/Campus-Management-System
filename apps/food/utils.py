from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_order_receipt_email(order):
    """
    Send order receipt email to the food stall
    
    Args:
        order: FoodOrder instance
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Check if stall has an email address
        if not order.stall.email:
            logger.warning(f"Stall {order.stall.name} does not have an email address configured")
            return False
        
        # Get order items
        order_items = order.items.select_related('food_item').all()
        
        # Calculate subtotal and tax
        subtotal = float(order.total_price) / 1.05  # Assuming 5% tax
        tax = float(order.total_price) - subtotal
        
        # Get customer name
        if order.student:
            customer_name = order.student.name
            customer_email = order.student.email
        elif order.user:
            customer_name = order.user.get_full_name() or order.user.email
            customer_email = order.user.email
        else:
            customer_name = "Guest"
            customer_email = "N/A"
        
        # Get payment method display name
        payment_method = dict(order.PAYMENT_METHOD_CHOICES).get(order.payment_method, 'Cash on Delivery')
        
        # Prepare context for email template
        context = {
            'order': order,
            'order_items': order_items,
            'stall': order.stall,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'payment_method': payment_method,
            'subtotal': subtotal,
            'tax': tax,
        }
        
        # Render HTML email
        html_content = render_to_string('food/emails/order_receipt.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        subject = f'New Order #{order.id} - {order.stall.name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [order.stall.email]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order receipt email sent to {order.stall.email} for order #{order.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order receipt email for order #{order.id}: {str(e)}")
        return False


def send_order_confirmation_to_customer(order):
    """
    Send order confirmation email to the customer
    
    Args:
        order: FoodOrder instance
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Get customer email
        if order.student and order.student.email:
            customer_email = order.student.email
            customer_name = order.student.name
        elif order.user and order.user.email:
            customer_email = order.user.email
            customer_name = order.user.get_full_name() or order.user.email
        else:
            logger.warning(f"No email address found for order #{order.id}")
            return False
        
        # Get order items
        order_items = order.items.select_related('food_item').all()
        
        # Calculate subtotal and tax
        subtotal = float(order.total_price) / 1.05  # Assuming 5% tax
        tax = float(order.total_price) - subtotal
        
        # Get payment method display name
        payment_method = dict(order.PAYMENT_METHOD_CHOICES).get(order.payment_method, 'Cash on Delivery')
        
        # Prepare context for email template
        context = {
            'order': order,
            'order_items': order_items,
            'stall': order.stall,
            'customer_name': customer_name,
            'payment_method': payment_method,
            'subtotal': subtotal,
            'tax': tax,
        }
        
        # Render HTML email
        html_content = render_to_string('food/emails/order_confirmation.html', context)
        text_content = strip_tags(html_content)
        
        # Create email
        subject = f'Order Confirmation #{order.id} - {order.stall.name}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [customer_email]
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=recipient_list
        )
        email.attach_alternative(html_content, "text/html")
        
        # Send email
        email.send()
        
        logger.info(f"Order confirmation email sent to {customer_email} for order #{order.id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for order #{order.id}: {str(e)}")
        return False
