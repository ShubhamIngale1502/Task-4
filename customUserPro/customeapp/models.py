from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    
    GENDER = [
        ('male','male'),
        ('female','female'),
        ('other','other')
    ]
    ROLES = [
        ('manager','manager'),
        ('team_leader', 'team_leader'),
        ('developer','developer'),
    ]
    gender = models.CharField(max_length = 45, choices= GENDER, default = 'male')
    address = models.TextField(blank = True, null = True)
    pincode = models.IntegerField(blank = True, null = True)
    city = models.CharField(max_length = 45)
    contact = PhoneNumberField(region = 'IN',blank = True, null = True)
    role  = models.CharField(max_length = 45,choices = ROLES, default = 'manager')
    company = models.CharField(max_length = 40)

