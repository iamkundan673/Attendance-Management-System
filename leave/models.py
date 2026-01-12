from django.db import models
from cloudinary.models import CloudinaryField
from ams.models import Adduser

# Create your models here.
# leave request model

LEAVE_CHOICES = [
    ('sick', 'Sick Leave'),
    ('casual', 'Casual Leave'),
    ('paid', 'paid Leave'),
    ('unpaid', 'unpaid Leave'),
]
class LeaveRequest(models.Model):
    employee = models.ForeignKey(Adduser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    leave_type = models.CharField(max_length=20, choices=LEAVE_CHOICES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
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
    reason = models.TextField(null=True, blank=True)
    alternate_contact = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.leave_type} - {self.status}"
