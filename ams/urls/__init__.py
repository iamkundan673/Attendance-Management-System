from django.urls import path, include

urlpatterns = [
    path('auth/', include('ams.urls.auth')),
    path('user/', include('ams.urls.user')),
    path('admin/', include('ams.urls.admin')),
    # path('attendance/', include('ams.urls.attendance')),
    # path('dashboard/', include('ams.urls.dashboard')),
    path('notification/', include('ams.urls.notification')),
]