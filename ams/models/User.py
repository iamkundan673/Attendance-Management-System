from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField



class Adduser(AbstractUser):
    Full_Name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    employee_id = models.CharField(max_length=20,null=True ,unique=True)
    # role = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=64, blank=True, null=True)

    profile_picture = CloudinaryField(
        'profile_picture',
        resource_type='image',
        folder='profile_pictures',
        null=True,
        blank=True
    )
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True,blank=True)
    def __str__(self):
        return self.username