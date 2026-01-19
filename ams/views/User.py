from ams.serializer import UserLoginSerializer
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from django.shortcuts import get_object_or_404
from ams.models.User import Adduser
from ams.models import Role
from cloudinary.uploader import destroy
from rest_framework import status
import json
from django.http import JsonResponse
from ams.services import notify
from ams.serializer import AdduserSerializer
from django.core.mail import send_mail
from rest_framework.permissions import IsAdminUser


@csrf_exempt
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def user_login_api(request):

    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data["user"]

    # SAME TOKEN LOGIC
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
        'success': True,
        'token': access_token,
        'is_staff': user.is_staff,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })


#----------------------------------------
# add profile picture of user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_profile_picture_api(request, user_id):
    target_user = get_object_or_404(Adduser, id=user_id)

    #  Permission rules
    if request.user != target_user and not request.user.is_staff:
        return Response(
            {"success": False, "error": "You are not allowed to update this profile"},
            status=status.HTTP_403_FORBIDDEN
        )

    profile_picture = request.FILES.get("profile_picture")
    if not profile_picture:
        return Response(
            {"success": False, "error": "No profile picture provided"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not profile_picture.content_type.startswith("image/"):
        return Response(
            {"success": False, "error": "Only image files are allowed"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Remove old picture
    if target_user.profile_picture:
        destroy(target_user.profile_picture.public_id)

    target_user.profile_picture = profile_picture
    target_user.save()

    return Response({
        "success": True,
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": target_user.profile_picture.url
    })
#view of user profile picture
@api_view(["GET"])
@permission_classes([AllowAny])
def get_profile_picture_api(request, user_id):
    user = get_object_or_404(Adduser, id=user_id)

    # Optional: allow only user themselves or admin
    if request.user != user and not request.user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    if not user.profile_picture:
        return Response(
            {"success": False, "error": "User has no profile picture"},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response({
        "success": True,
        "profile_picture_url": user.profile_picture.url
    }, status=status.HTTP_200_OK)

#---------------------------------------
# edit user ,role ra status like active or disable garcha admin le
@csrf_exempt
@api_view(["POST"])
def edit_user_api(request, user_id):
    try:
        user = Adduser.objects.get(id=user_id)
    except Adduser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    changes = []  # 🔹 track what changed


    if 'is_active' in data:
        user.is_active = data['is_active']
        changes.append("Account status updated")

    if 'email' in data:
        user.email = data['email']
        changes.append("Email updated")

    if 'contact_number' in data:
        user.contact_number = data['contact_number']
        changes.append("Contact number updated")

    if 'role' in data:
        try:
            role_obj = Role.objects.get(name__iexact=data['role'])
            user.role = role_obj
            changes.append("Role updated")
        except Role.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)
    user.save()
       #  SEND NOTIFICATION TO USER
    if changes:
        notify(
            user=user,
            title="Account Updated",
            message="Your account details were updated by admin: " + ", ".join(changes),
            type="account"
        )

    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'role': user.role.name if user.role else None,
            'contact_number': user.contact_number,
        }
    })


@csrf_exempt
@api_view(["GET"])
def user_list_api(request):
    users = Adduser.objects.all()
    serializer = AdduserSerializer(users, many=True)

    active_users = []
    disabled_users = []

    for u in serializer.data:
        # use get() to avoid KeyError
        
        is_active = u.get('is_active', False)
        if is_active:
            active_users.append(u)
        else:
            disabled_users.append(u)

    return Response({
        'success': True,
        'active_users': active_users,
        'disabled_users': disabled_users
    })


# deleting the user
@csrf_exempt
def user_delete(request, user_id):
    if request.method != 'DELETE':
        return JsonResponse(
            {'success': False, 'error': 'DELETE request required'},
            status=400
        )

    try:
        user = Adduser.objects.get(id=user_id)
        user.delete()
        return JsonResponse(
            {'success': True, 'message': 'User deleted successfully'},
            status=200
        )

    except Adduser.DoesNotExist:
        return JsonResponse(
            {'success': False, 'error': 'User not found'},  
            status=404
        )
# only disable the user 
@csrf_exempt
def user_disable_api(request, user_id):
    if request.method != 'POST':  # POST for disabling
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)

    try:
        user = Adduser.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return JsonResponse({'success': True, 'message': 'User disabled successfully'})
    except Adduser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)


 
#--------------------------------------------------#
from ams.models.Role import Role
# user banaune by admin
def generate_temp_password(length=8):
    import secrets, string
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user_api(request):

    data = request.data

    Full_Name = data.get("fullname") or data.get("Full_Name")
    email = data.get("email")
    role_name = data.get("role", "").strip() 
    contact_number = data.get("contact_number", "")
    address = data.get("address", "")
    employee_id = data.get("employee_id", "")

    if not email:
        return Response({"detail": "Email is required"}, status=400)

    if not Full_Name:
        return Response({"detail": "Fullname is required"}, status=400)
    
    if not employee_id:
        return Response({"detail": "Employee ID is required"}, status=400)
    
    if not contact_number:
        return Response({"detail": "Contact number is required"}, status=400)
    
    if not address:
        return Response({"detail": "Address is required"}, status=400)

    username = email.split("@")[0]

    if User.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists"}, status=400)

    if User.objects.filter(email=email).exists():
        return Response({"detail": "Email already exists"}, status=400)
    
    if User.objects.filter(employee_id=employee_id).exists():
        return Response({"detail": "Employee ID already exists"}, status=400)

    temp_password = generate_temp_password()

    # CORRECT USER CREATION
    user = User.objects.create_user(
        username=username,
        email=email,
        password=temp_password,
    )
    user.Full_Name = Full_Name
    user.contact_number=contact_number
    user.address=address
    user.employee_id=employee_id
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True

    if role_name:
        role_obj, created = Role.objects.get_or_create(name=role_name)
        user.role = role_obj
    else:
        user.role = None  # optional: no role

    user.save()

    user.save()

    # Send email
    subject = "Your Account Login Details"
    message = f"""
Hello {Full_Name},

Your account has been created successfully.

Username: {username}
Temporary Password: {temp_password}

Please log in and change your password immediately.
"""

    send_mail(subject, message, 'kundanchapagain555@gmail.com', [email])

    serializer = AdduserSerializer(user)

    return Response({
        "success": True,
        "message": "User created successfully",
        "user": serializer.data
    })


#-----------------------------------------------------------
# Reseting the password of the user by admin
#-----------------------------------------------------------
from ams.services import notify
@csrf_exempt
def admin_reset_password(request, user_id):
    if request.method != 'PUT':
        return JsonResponse({'success': False, 'error': 'PUT request required'}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    password = data.get('password')
    confirm_password = data.get('confirm_password')

    # Validation
    if not password or not confirm_password:
        return JsonResponse({'success': False, 'error': 'Password and confirm password are required.'}, status=400)

    if password != confirm_password:
        return JsonResponse({'success': False, 'error': 'Passwords do not match.'}, status=400)

    # Get user by user_id from URL
    try:
        user = Adduser.objects.get(id=user_id)
    except Adduser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found.'}, status=404)

    # Update password
    user.set_password(password)
    user.save()

    notify(
        user=user,
        title="Password Changed",
        message="Your account password was reset by the admin. Please login and change it if needed.",
        type="security"
    )


    # Send new password via email
    subject = "Your Account Password Has Been Updated"
    message = f"""
Hello {user.username},

Your account password has been updated by the admin.

Login Details:
------------------------
Username: {user.username}
Email: {user.email}
New Password: {password}

Please log in using this password and change it if needed.

Thanks,
The Team
"""
    try:
        send_mail(subject, message, 'kundanchapagain555@gmail.com', [user.email])
    except:
        return JsonResponse({'success': True, 'message': 'Password updated, but failed to send email.'})

    return JsonResponse({'success': True, 'message': 'Password updated successfully'})