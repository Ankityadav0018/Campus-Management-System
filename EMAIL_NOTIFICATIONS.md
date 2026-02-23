# Email Notification System for Food Ordering

## ✅ Implementation Complete

The food ordering system now has a comprehensive email notification system that sends emails to both food stall vendors and customers when orders are placed.

---

## 📧 Features Implemented

### 1. **Dual Email Notifications**
- **Vendor/Stall Receipt**: Food stalls receive detailed order receipts via email
- **Customer Confirmation**: Customers receive order confirmation emails

### 2. **Professional HTML Email Templates**
- Beautiful, responsive email design
- Order details with itemized list
- Total amount and payment method
- Pickup time slot information
- Special instructions (if any)

### 3. **Email Utility Functions**
Location: `apps/food/utils.py`

#### Functions:
- `send_order_receipt_email(order)` - Sends receipt to food stall
- `send_order_confirmation_to_customer(order)` - Sends confirmation to customer

---

## 📁 Files Created/Modified

### New Files:
1. **`apps/food/utils.py`** - Email sending utility functions
2. **`apps/food/templates/food/emails/stall_order_receipt.html`** - Stall receipt template
3. **`apps/food/templates/food/emails/customer_order_confirmation.html`** - Customer confirmation template

### Modified Files:
1. **`apps/food/views.py`** - Integrated email sending in `place_order` view
2. **`apps/food/models.py`** - FoodStall model already has `email` field

---

## 🔧 How It Works

### When an order is placed:

1. **Order Creation**: Customer places an order through the UI
2. **Stall Notification**: 
   - Email sent to `FoodStall.email` address
   - Contains full order details and items
   - Shows customer information
3. **Customer Notification**:
   - Email sent to `request.user.email`
   - Order confirmation with receipt
   - Pickup time and stall location

### Email Flow:
```
Customer Places Order
        ↓
Order Saved to Database
        ↓
    ┌───────────────────────┐
    │                       │
    ↓                       ↓
Send to Stall          Send to Customer
(Vendor Email)         (User Email)
```

---

## 📋 Email Configuration

### Current Setup (Development):
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```
- Emails are printed to the **console/terminal**
- Perfect for testing and development

### Production Setup:
To enable real email sending, update `campus_project/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use app password, not regular password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
```

#### For Gmail:
1. Enable 2-Factor Authentication on your Google account
2. Generate an **App Password** (Google Account → Security → App Passwords)
3. Use the app password in `EMAIL_HOST_PASSWORD`

#### For Other Providers:
- **Outlook/Hotmail**: `smtp.office365.com`, Port 587
- **Yahoo**: `smtp.mail.yahoo.com`, Port 587
- **SendGrid**: `smtp.sendgrid.net`, Port 587
- **AWS SES**: Configure with AWS credentials

---

## 🧪 Testing

### Development Testing:
1. Start the Django server: `python manage.py runserver`
2. Place an order through the food ordering UI
3. Check the **terminal/console** output - you'll see the email content printed
4. Look for messages like:
   ```
   📧 Order receipt sent to [Stall Name]
   📧 Order confirmation sent to your email
   ```

### Production Testing:
1. Configure SMTP settings (see above)
2. Ensure food stalls have valid email addresses
3. Ensure users have valid email addresses
4. Place test orders and verify emails arrive

---

## ✨ Email Content

### Stall Receipt Email:
- **Subject**: "New Order #[ORDER_ID] - [Customer Name]"
- **Content**:
  - Order ID and date/time
  - Customer name and contact
  - Itemized list of food items
  - Quantities and prices
  - Total amount
  - Payment method
  - Pickup time slot
  - Special instructions

### Customer Confirmation Email:
- **Subject**: "Order Confirmation #[ORDER_ID] - [Stall Name]"
- **Content**:
  - Order confirmation message
  - Stall name and location
  - Order summary
  - Pickup time
  - Total amount
  - Special instructions

---

## 🔍 Error Handling

The email system is designed to fail gracefully:
- If email sending fails, the order is **still created**
- User sees a success message for the order
- Error is logged but doesn't break the ordering process
- Optional: Success messages show if emails were sent

---

## 📊 Database Requirements

### FoodStall Model Fields Used:
- `email` - Vendor/stall email address (already exists)
- `name` - Stall name
- `location` - Stall location (if available)

### User Model Fields Used:
- `email` - Customer email address
- `username` or `get_full_name()` - Customer name

---

## 🚀 Future Enhancements

Potential additions:
1. **SMS notifications** alongside emails
2. **Order status update emails** (preparing, ready, completed)
3. **Daily sales summary** emails to vendors
4. **Promotional emails** for special offers
5. **Email preferences** for users to opt-in/opt-out
6. **Email templates** with custom branding per stall
7. **Automated reminders** before pickup time

---

## 📝 Usage in Code

```python
from apps.food.utils import send_order_receipt_email, send_order_confirmation_to_customer

# After creating an order
order = FoodOrder.objects.create(...)

# Send emails
send_order_receipt_email(order)  # To vendor
send_order_confirmation_to_customer(order)  # To customer
```

---

## ⚠️ Important Notes

1. **Email Addresses Required**: Ensure all food stalls have valid email addresses in the database
2. **User Email**: Users must have email addresses registered
3. **SMTP Limits**: Most providers have daily sending limits (Gmail: 500/day for free accounts)
4. **Spam Filters**: Test emails might go to spam initially
5. **App Passwords**: Never commit real passwords to version control - use environment variables

---

## 🎯 Summary

✅ Email notifications implemented for food orders  
✅ Dual notifications: vendor receipt + customer confirmation  
✅ Professional HTML email templates  
✅ Graceful error handling  
✅ Ready for production with SMTP configuration  
✅ Currently logs to console for development testing  

The system is **production-ready** and just needs SMTP configuration to start sending real emails!
