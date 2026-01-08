from django.db import models

# Create your models here.
# #storing the ip
class OfficeIP(models.Model):
    ip_address = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.ip_address
    


