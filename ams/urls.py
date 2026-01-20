from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Attendance System is live!")

urlpatterns = [
    path('',home,name='home'),
    path('auth/', include('ams.urls.auth')),
    path('user/', include('ams.urls.user')),
    path('admin/', include('ams.urls.admin')),
    path('notification/', include('ams.urls.notification')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
