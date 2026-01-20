from django.urls import path
from ams.views.Attendance  import (attendance_history_api,all_attendance_api,attendance_by_user,my_attendance_summary_api,present_absent_summary_api)
from ams.views.User import create_user_api,user_list_api,user_disable_api,user_delete,admin_reset_password,edit_user_api
from ams.views.Holiday import holiday_create_api,holiday_delete_api
from ams.views.Role import create_role_api,get_roles_api,edit_role_api
urlpatterns = [
    path('create-user/', create_user_api, name='get_client_ip_view'),
    path('view-users/', user_list_api, name='user_list_api'),
    path('disable-user/<int:user_id>/', user_disable_api, name='user_disable_api'),
    path('delete-user/<int:user_id>/', user_delete, name='user_delete_api'),
    path('change-password/<int:user_id>/', admin_reset_password, name='user_delete_api'),
    path('attendance-history/', all_attendance_api, name='all_attendence_api'),
    path('edit-user/<int:user_id>/', edit_user_api, name='edit_user_api'),
    path('user-attendance-details/<int:user_id>/', attendance_by_user, name='attendance_history'),
    path('uleavedetails/',my_attendance_summary_api,name='attendence_summary_of_user'),
    path('alleavedetails/',present_absent_summary_api,name='present_absent_summary_api'),
    path('create-holiday/',holiday_create_api,name='holiday_create_api'),
    path('delete-holiday/date/',holiday_delete_api,name='holiday_delete_api'),
    path('create-role/', create_role_api, name='create_role_api'),
    path('list-role/',get_roles_api, name='get_roles_api'),
    path('edit-role/<int:role_id>/', edit_role_api, name='edit_role_api'),
]
