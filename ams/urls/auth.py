from ams.views import CustomTokenObtainPairView
from django.urls import path
from ams.views import Token  as views
from ams.views.User import user_login_api
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_api, name='logout_api'),
    path('login/',user_login_api,name="user_login_api"), # yesle user login garxa
]