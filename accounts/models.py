from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin,AbstractUser
from notifications.signals import notify
from notifications.models import Notification  # Assurez-vous d'importer le modèle Notification de l'application de notifications
class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, password,email,sexe,user_category,lieu_de_residence,date_naissance,date_inscription,telephone,promotion,photo, **kwargs):
        """
        Creates and saves a User with the given phone and password.
        """
        email=self.normalize_email(email)
        if not email:
            raise ValueError('Users must have email')
        
        user = self.model(
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo
        )

        user.is_active = True
        user.admin = False
        user.staff = False

        user.set_password(password)
        user.save()

        return user
    

    def create_staffuser(self, first_name, last_name,password,email,sexe,user_category,lieu_de_residence,date_naissance,date_inscription,telephone,promotion,photo):

        email=self.normalize_email(email)
        user = self.create_user(
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo,
            password=password
        )

        user.staff = True
        user.is_active = True


        user.save()
        return user
    
    def create_superuser(self, first_name, last_name, email,password,sexe,user_category,lieu_de_residence,date_naissance,date_inscription,telephone,promotion,photo):
        email=self.normalize_email(email)
        user = self.create_user(
            
            first_name = first_name,
            last_name = last_name,
            email=email,
            sexe=sexe,
            user_category=user_category,
            lieu_de_residence=lieu_de_residence,
            date_naissance=date_naissance,
            date_inscription=date_inscription,
            telephone=telephone,
            promotion=promotion,
            photo=photo,
            password=password
            
            
        )
        
        

        user.admin = True
        user.staff = True
        user.is_active = True
        
        user.save()
        return user




class User(AbstractBaseUser,PermissionsMixin):
    # ROLES = (('student', 'Student'), ('FORMATEUR EXTAINE', 'FORMATEUR EXTAINE'),('PERSONNEL','PERSONNEL'),('STAGIAIRE','STAGIAIRE'))
    first_name=models.CharField(max_length=255)
    last_name=models.CharField(max_length=255)
    email=models.EmailField(max_length=255,unique=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    user_category=models.CharField(max_length=25,blank=False,null=False)
    sexe=models.CharField(blank=False,max_length=50)
    lieu_de_residence=models.CharField(max_length=100,null=True,blank=True)
    date_naissance=models.DateField(blank=True,null=True)
    date_inscription=models.DateField(blank=True,null=True)
    telephone=models.IntegerField()
    promotion=models.CharField(max_length=255,null=True,blank=True)
    photo=models.ImageField(upload_to='PROFIL_IMG')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','sexe',"user_categlory",'lieu_de_residence','date_naissance','date_inscription','telephone',"promotion"]

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin


    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True
    
    def send_notification(self, message):
        notify.send(
            self,
            recipient=self,
            verb=message
        )

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
       return self.first_name

    
