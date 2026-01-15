from django.db import models
from .User import Adduser
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

