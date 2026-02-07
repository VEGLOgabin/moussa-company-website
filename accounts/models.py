# models.py - Update the USER_TYPES and add admin-specific fields if needed
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from notifications.signals import notify

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, first_name, last_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('admin', 'Admin'),
        ('superadmin', 'Super Admin'),  # Added superadmin
        ('manager', 'Manager'),         # Added manager level
        ('customer', 'Customer'),
    )
    
    ADMIN_ROLES = (
        ('superadmin', 'Super Administrateur'),
        ('content', 'Administrateur Contenu'),
        ('order', 'Administrateur Commandes'),
        ('support', 'Support Client'),
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    sex = models.CharField(max_length=50, blank=True, null=True)  # Made optional for admin
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    admin_role = models.CharField(max_length=20, choices=ADMIN_ROLES, blank=True, null=True)  # New field
    birthdate = models.DateField(blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='PROFIL_IMG', blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)  # New field for admin
    can_manage_users = models.BooleanField(default=False)  # New field
    can_manage_products = models.BooleanField(default=False)  # New field
    can_manage_orders = models.BooleanField(default=False)  # New field

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def send_notification(self, message):
        notify.send(self, recipient=self, verb=message)
    
    def is_admin(self):
        return self.user_type in ['admin', 'superadmin', 'manager']
    
    def is_superadmin(self):
        return self.user_type == 'superadmin'
    
    def is_customer(self):
        return self.user_type == 'customer'
    
    def get_admin_display_name(self):
        """Get formatted admin display name"""
        if self.is_superadmin():
            return f"{self.get_full_name()}"
        elif self.is_admin():
            role_display = self.get_admin_role_display() if self.admin_role else ""
            return f"{self.get_full_name()} ({role_display})"
        else:
            return self.get_full_name()
    
    def has_admin_permission(self, permission):
        """Check specific admin permission"""
        if permission == 'manage_users':
            return self.can_manage_users
        elif permission == 'manage_products':
            return self.can_manage_products
        elif permission == 'manage_orders':
            return self.can_manage_orders
        return False
    
    def admin_permissions(self):
        """Get list of admin permissions"""
        permissions = []
        if self.can_manage_users:
            permissions.append('manage_users')
        if self.can_manage_products:
            permissions.append('manage_products')
        if self.can_manage_orders:
            permissions.append('manage_orders')
        return permissions











# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from notifications.signals import notify  # You can access a user’s notifications like this: request.user.notifications.unread()

# class UserManager(BaseUserManager):
#     def create_user(self, email, first_name, last_name, password=None, **extra_fields):
#         if not email:
#             raise ValueError("Email is required")
#         email = self.normalize_email(email)
#         user = self.model(
#             email=email,
#             first_name=first_name,
#             last_name=last_name,
#             **extra_fields
#         )
#         user.set_password(password)
#         user.save()
#         return user

#     def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         extra_fields.setdefault("user_type", "admin")

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True")

#         return self.create_user(email, first_name, last_name, password, **extra_fields)


# class User(AbstractBaseUser, PermissionsMixin):
#     USER_TYPES = (
#         ('admin', 'Admin'),
#         ('customer', 'Customer'),
#     )

#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     sex = models.CharField(max_length=50)
#     user_type = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
#     birthdate = models.DateField(blank=True, null=True)
#     registration_date = models.DateField(auto_now_add=True)
#     phone_number = models.CharField(max_length=20)
#     photo = models.ImageField(upload_to='PROFIL_IMG', blank=True, null=True)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)  # Needed for Django admin

#     objects = UserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name']

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.email})"
    
#     def get_full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def send_notification(self, message):
#         notify.send(self, recipient=self, verb=message)

#     def is_admin(self):
#         return self.user_type in ['admin', 'superadmin', 'manager']

