from .models import Notification

def notify(user, title, message, type='system'):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type
    )
