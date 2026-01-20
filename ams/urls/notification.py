from django.urls import path
from ams.views.Notification  import my_notifications,mark_as_read


urlpatterns = [
    path('notifications/', my_notifications, name='my_notifications'),
    path('mark-as-read/<int:id>/read/', mark_as_read, name='mark_as_read'),
]