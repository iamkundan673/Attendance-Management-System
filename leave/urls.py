from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('lea/',views.list_all_leaves_api,name="list_all_leaves_api"),
    path('submitleave/',views.submit_leave_api,name="submit_leave_api"),
    path('leaveaction/<int:leave_id>/action/',views.leave_action_api,name="leave_action_api"),
    path('userleave/', views.user_leaves_api, name='user_leaves-api'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
