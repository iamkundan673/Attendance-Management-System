from django.db import models

class Holiday(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        if self.end_date:
            return f"{self.start_date} to {self.end_date} - {self.description[:50]}..."
        return f"{self.start_date} - {self.description[:50]}..."
