from django.db import models
from django.utils import timezone
from accounts.models import User
from django.core.validators import MinValueValidator, MaxValueValidator






class Product(models.Model):
    name = models.CharField(max_length=255)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    available = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=100, default="FCFA")
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    
    
    # ✅ NEW FIELD
    is_active = models.BooleanField(default=True)
    
    
    def average_rating(self):
        """Calculate average rating for the product"""
        ratings = self.ratings.all()
        if ratings:
            return round(sum(r.rating for r in ratings) / len(ratings), 1)
        return 0
    
    def rating_count(self):
        """Get total number of ratings"""
        return self.ratings.count()
    
    def user_rating(self, user):
        """Get user's rating for this product"""
        try:
            return self.ratings.get(user=user).rating
        except ProductRating.DoesNotExist:
            return 0
        
    def __str__(self):
        return self.name

        
        
        
    
class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['product', 'user']  # One rating per user per product
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating} stars"






class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),       # Order created, not paid
        ('processing', 'En cours'),      # Payment verification in progress
        ('paid', 'Payé'),                # Payment successful
        ('shipped', 'Expédié'),          # Order shipped
        ('delivered', 'Livré'),          # Order delivered
        ('cancelled', 'Annulé'),         # Order cancelled
    ]

    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=100, default="FCFA")
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Our internal transaction ID for reference (never null)
    internal_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        blank=False,
        null=False,
        db_index=True
    )

    def __str__(self):
        return f"Order {self.id} by {self.ordered_by}"




class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_products')  # Add related_name here
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} for Order {self.order.id}"



class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    photo = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name

class Partner(models.Model):
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='partners')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='partners/')
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"

class BlogPost(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogposts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    cover_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    

   
class PaymentHistory(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours de vérification'),
        ('success', 'Succès'),
        ('failed', 'Échoué'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    # 🔐 CRITICAL IDENTIFIERS
    internal_transaction_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True
    )
    kkiapay_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True
    )

    payment_method = models.CharField(
        max_length=100,
        default="MOMO"
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return (
            f"{self.user.first_name} | "
            f"{self.amount} {self.order.currency} | "
            f"{self.status}"
        )
 
    
    
    




# -------------------- USER ACTION LOG --------------------
class UserActionLog(models.Model):
    LEVEL_CHOICES = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('DEBUG', 'Debug'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='action_logs')
    action = models.TextField()  # Description of the action
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='INFO')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        user_str = f"{self.user}" if self.user else "Anonymous"
        return f"[{self.level}] {user_str} - {self.action[:50]}"