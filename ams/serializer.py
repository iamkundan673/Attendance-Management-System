from rest_framework import serializers
from .models import Adduser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        #  Add role info
        token["is_staff"] = user.is_staff
        token["user_id"] = user.id
        return token
    


# yo aile bharkhar haleko maile 
# serializer.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True
    )

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password", "").strip()

        # SAME VALIDATION AS VIEW
        if not username or not password:
            raise serializers.ValidationError(
                "Username and password are required"
            )

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                "Invalid username or password"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "Account is inactive"
            )

        # STORE user for view
        attrs["user"] = user
        return attrs
