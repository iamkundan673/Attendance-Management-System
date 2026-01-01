from rest_framework import serializers
from .models import Adduser

class AdduserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adduser
        fields = [
            'id',
            'Full_Name',
            'username',
            'email',
            'role',
            'contact_number',
            'address',
            'employee_id',
        ]
        read_only_fields = ['id', 'username', 'employee_id']

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        #  Add role info
        token["is_staff"] = user.is_staff
        token["user_id"] = user.id
        return token