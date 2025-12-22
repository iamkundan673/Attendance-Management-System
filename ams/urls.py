"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('login/',views.user_login_api,name="user_login_api"),
    path('dashboard/', views.dashboard_api, name='user-dashboard'),
    path('attendance/', views.attendance_api, name='mark_attendance'),
    path('history/', views.attendance_history_api, name='attendance_history_api'),
    path('crt/', views.create_user_api, name='get_client_ip_view'),
    path('view/', views.user_list_api, name='user_list_api'),
    path('delete/<int:user_id>/', views.user_delete_api, name='user_delete_api'),
    path('update/<int:user_id>/', views.admin_reset_password, name='user_delete_api'),
    path('leave/', views.submit_leave_api, name='submit_leave_api'),
    path('lisapp/', views.list_all_leaves_api, name='leave_list_admin_api'),
    path('reject/<int:leave_id>/', views.leave_action_api, name='leave_action_api'),
    path('adminattendancehistory/', views.all_attendance_api, name='all_attendence_api'),
    path('edituser/<int:user_id>/', views.edit_user_api, name='edit_user_api'),
    path('details/<int:user_id>/', views.attendance_by_user, name='attendance_history'),
    path('userleave/', views.user_leaves_api, name='user_leaves-api'),
    path('uleavedetails/',views.my_attendance_summary_api,name='attendence_summary_of_user'),
    path('alleavedetails/',views.present_absent_summary_api,name='present_absent_summary_api'),

    # path('ip/', views.ipcheck, name='edi'),
    # path('ams/', include('ams.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)