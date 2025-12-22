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
            'profile_picture',
        ]
        read_only_fields = ['id', 'username']

