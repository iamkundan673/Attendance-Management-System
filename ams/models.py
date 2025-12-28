from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class Adduser(AbstractUser):
    Full_Name = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    # role = models.CharField(max_length=50, blank=True)
    password = models.CharField(max_length=128)
    token = models.CharField(max_length=64, blank=True, null=True)

    profile_picture = CloudinaryField(
        'profile_picture',
        resource_type='image',
        null=True,
        blank=True
    )


    ROLE_CHOICES=[
        ('It','It'),
        ('Backend Developer','Backend Developer'),
        ('Frontend Developer','Frontend Developer'),
        ('Fullstack Developer','Fullstack Developer'),
        ('UI/UX Designer','UI/UX Designerr'),
        ('Digital Marketing','Digital Marketing'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='Frontend')
    def __str__(self):
        return self.username
    
    
# ams/models.py
from django.db import models

class Attendance(models.Model):
    user = models.ForeignKey(Adduser, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status = models.CharField(max_length=20, default="On Time")  # On Time, Late, etc.

    status= models.CharField(
        max_length=10,
        choices=[
            ('Present','Present'),
            ('Absent','Absent'),
        ]
    )

    def __str__(self):
        return f"{self.user.username} - {self.date}"
    


    
    # NEW field for Present / Absent
    ATT_PRESENT = 'Present'
    ATT_ABSENT = 'Absent'
    ATTENDANCE_CHOICES = [
        (ATT_PRESENT, 'Present'),
        (ATT_ABSENT, 'Absent'),
    ]
    attendance_status = models.CharField(max_length=10,choices=ATTENDANCE_CHOICES,default=ATT_PRESENT)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.attendance_status} - {self.status}"


from django.db import models
from django.contrib.auth.models import AbstractUser

LEAVE_CHOICES = [
    ('sick', 'Sick Leave'),
    ('casual', 'Casual Leave'),
    ('earned', 'Earned Leave'),
]

# leave request model
class LeaveRequest(models.Model):
    employee = models.ForeignKey(Adduser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICES)
    # start_date = models.DateField()
    # end_date = models.DateField()
    document = CloudinaryField(
        'document',
        resource_type='raw',  # important for PDFs and docs
        folder='leave_docs',
        type='upload',
        null=True,
        blank=True
    )
    status = models.CharField(max_length=10, choices=[('pending','Pending'), ('approved','Approved'), ('rejected','Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reject_reason = models.TextField(null=True, blank=True) 

    def __str__(self):
        return f"{self.full_name} - {self.leave_type} - {self.status}"

# #storing the ip
class OfficeIP(models.Model):
    ip_address = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.ip_address

# holiday model
class Holiday(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        if self.end_date:
            return f"{self.start_date} to {self.end_date} - {self.description[:50]}..."
        return f"{self.start_date} - {self.description[:50]}..."