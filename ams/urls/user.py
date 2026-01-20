from django.urls import path
from ams.views.Dashboard  import dashboard_api
from ams.views.Attendance  import attendance_api,auto_mark_absent,attendance_history_api
from ams.views.User import upload_profile_picture_api,get_profile_picture_api
from ams.views.Holiday import holiday_list_api
urlpatterns = [
    path('dashboard/', dashboard_api, name='user-dashboard'),
    path('attendance/', attendance_api, name='mark_attendance'),
    path("auto-mark-absent/<str:secret_key>/", auto_mark_absent, name="auto_mark_absent"),
    path('upload-profile-picture/<int:user_id>/',upload_profile_picture_api,name='upload_profile_picture_api'),
    path('holiday-list/',holiday_list_api,name='holiday_list_api'),
    path('view-profile-picture/<int:user_id>/',get_profile_picture_api,name='get_profile_picture_api'),
    path('attendance/', attendance_history_api, name='attendance_history_api'),
]
