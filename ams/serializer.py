from rest_framework import serializers
from .models import Adduser,Role
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class AdduserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Adduser
#         fields = [
#             'id',
#             'Full_Name',
#             'username',
#             'email',
#             'role',
#             'contact_number',
#             'address',
#             'employee_id',
#         ]
#         read_only_fields = ['id', 'username', 'employee_id']


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']


class AdduserSerializer(serializers.ModelSerializer):
    # Instead of raw FK id, show the role name
    role = serializers.CharField(source='role.name', read_only=True)
    
    # Optional: allow inputting a new role by name
    role_input = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Adduser
        fields = [
            'id',
            'Full_Name',
            'username',
            'email',
            'role',        # Read-only, shows the current role name
            # 'role_input',  # Write-only, used to create/update role dynamically
            'contact_number',
            'address',
            'is_active',
            'employee_id',
        ]
        read_only_fields = ['id', 'username', 'employee_id','role']

    def create(self, validated_data):
        role_name = validated_data.pop('role_input', None)
        user = Adduser(**validated_data)
        
        # If password is passed in validated_data, you can handle it here
        password = validated_data.get('password')
        if password:
            user.set_password(password)

        # Handle dynamic role creation
        if role_name:
            role_obj, created = Role.objects.get_or_create(name=role_name.strip())
            user.role = role_obj

        user.save()
        return user

    def update(self, instance, validated_data):
        role_name = validated_data.pop('role_input', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if role_name:
            role_obj, created = Role.objects.get_or_create(name=role_name.strip())
            instance.role = role_obj

        instance.save()
        return instance
        
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


from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
