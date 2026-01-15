from django.db import models
from .User import Adduser

class Notification(models.Model):

    TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('holiday', 'Holiday'),
        ('security', 'Security'),
        ('attendance', 'Attendance'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(Adduser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=100)
    message = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"
