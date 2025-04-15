from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from datetime import datetime


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("You must set an email adress.")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_active"] = True
        kwargs["is_superuser"] = True
    
        self.create_user(email=email, password=password, **kwargs)





class Shopper(AbstractUser):
    username = None
    email = models.EmailField(max_length=240, unique=True)
    date_birth = models.DateField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["last_name", "first_name","date_birth"]
    objects = CustomUserManager()

ADRESS_FORMAT = """
{name}
{address_1}
{address_2}
{city}, {district}, {zip_code}


"""

class ShippingAddress(models.Model):
    user = models.ForeignKey(Shopper, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=240)
    address_1 = models.CharField(max_length=1024, help_text="Adresse de voirie et numéro de rue")
    address_2 = models.CharField(max_length=1024, help_text="Bâtiment, étage, lieu-dit...", blank=True)
    city = models.CharField(max_length=1024)
    district = models.CharField(max_length=550)
    zip_code = models.CharField(max_length=32)
    default = models.BooleanField(default=False)


    def __str__(self):
        return ADRESS_FORMAT.format(**self.__dict__).strip("\n")
    

    def set_default(self):
        self.user.shippingaddress_set.update(default=False)
        self.default = True
        self.save()