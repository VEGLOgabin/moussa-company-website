from django.db import models
from django.utils import timezone

from accounts.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    quantity = models.PositiveIntegerField(default=1)
    currency = models.CharField(max_length=100, default="XOF")
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)
    


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('processing', 'En cours'),
        ('shipped', 'Expédié'),
        ('delivered', 'Livré'),
        ('cancelled', 'Annulé'),
    ]

    ordered_by = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderProduct')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=100, default="XOF")
    ordered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')



class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    
    



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
        ('success', 'Succès'),
        ('failed', 'Échoué'),
        ('pending', 'En attente'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=100, default="CinetPay")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.amount} {self.order.currency} - {self.status}"

