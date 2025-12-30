# Create your views here.
from rest_framework.decorators import api_view,permission_classes,authentication_classes,parser_classes
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password,make_password
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Adduser,Attendance,LeaveRequest
import json
from django.http import JsonResponse
from django.core.mail import send_mail
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.utils import timezone
from .utils import get_client_ip, is_holiday
from datetime import date, datetime
from django.conf import settings
import os
from rest_framework import status 
from .serializer import AdduserSerializer
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.parsers import MultiPartParser, FormParser

#--------------------------
# user login 
#--------------------------
@csrf_exempt
@api_view(['POST'])
@authentication_classes([])  # disables authentication
@permission_classes([AllowAny])  # allows any user to call this view
def user_login_api(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not username or not password:
        return Response({'success': False, 'message': 'Username and password are required'}, status=400)

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'success': False, 'message': 'Invalid username or password'},
            status=401
        )

    if not user.is_active:
        return Response(
            {'success': False, 'message': 'Account is inactive'},
            status=403
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
        'success': True,
        'token': access_token,
        'is_staff':user.is_staff,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            
          
        }
    })
#-----------------------------------------------------------
# Reseting the password of the user by admin
#-----------------------------------------------------------
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

# Attendence page ko lagi,user specific data haru 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    """
    Return logged-in user info using JWT authentication, structured for frontend.
    """
    user = request.user  # DRF sets this from the JWT

    return Response({
        'user': {
            'userId': user.id,       # matches frontend's userId field
            'username': getattr(user, 'username', ''),  # matches frontend's name
            'email': user.email,
            'contactNumber': getattr(user, 'contact_number', ''),  # optional, if you have this field
            'role': getattr(user, 'role', ''),  # optional, if you have a role field
            'address': getattr(user, 'address', ''), 
            'employee_id': getattr(user, 'employee_id', ''), 
            
        },
        'success': True
    })

#----------------------tei mark attendence ho 
# @csrf_exempt
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def attendance_api(request):
#     user = request.user
#     user_ip = get_client_ip(request)

#     # Check if user is in the office network
#     if not is_in_office_network(user_ip):
#         return Response({'success': False, 'error': 'You are not in the office network'}, status=403)

#     # Check if already marked today
#     today = date.today()
#     if Attendance.objects.filter(user=user, date=today).exists():
#         return Response({'success': False, 'error': 'Attendance already marked today.'})

#     # Determine status based on check-in time
#     current_time = datetime.now().time()
#     status = "On Time" if current_time <= datetime.strptime("09:30:00", "%H:%M:%S").time() else "Late"

#     # Save attendance
#     attendance = Attendance.objects.create(
#         user=user,
#         ip_address=user_ip,
#         status=status,
#         date=today,
#         check_in_time=timezone.now()
#     )

#     return Response({
#         'success': True,
#         'attendance': {
#             'sn': attendance.id,
#             'date': attendance.date.strftime("%m/%d/%Y"),
#             'time': attendance.check_in_time.strftime("%H:%M:%S %p"),
#             'ip': attendance.ip_address,
#             'status': attendance.status
#         }
#     })


def is_within_time_window():
    now = datetime.now().time()  # current server time
    return settings.ATTENDANCE_START_TIME <= now <= settings.ATTENDANCE_END_TIME

# from .models import Holiday

# @csrf_exempt
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def attendance_api(request):
#     user = request.user
#     client_ip = get_client_ip(request)

#     if client_ip not in settings.ALLOWED_ATTENDANCE_IPS:
#         return Response({'success': False, 'error': 'Attendence can only be marked form the office network'}, status=403)
#     # if not is_within_time_window():
#     #     return Response({'success': False, 'error': 'Attendance can only be marked between 9:00 AM and 10:30 AM'}, status=403)
    
#     # Check if already marked today
#     today = date.today()
    
#     if is_holiday(today):
#         return Response({"success": False, "error": "Attendance cannot be marked on a holiday." }, status=403)
    
#     if Attendance.objects.filter(user=user, date=today).exists():
#         return Response({'success': False, 'error': 'Attendance already marked today.'})
    
#     # Determine punctuality status based on check-in time
#     current_time = datetime.now().time()
#     status = "On Time" if current_time <= datetime.strptime("09:30:00", "%H:%M:%S").time() else "Late"

#     # Save attendance (with new attendance_status field)
#     attendance = Attendance.objects.create(
#         user=user,
#         ip_address=client_ip,
#         status=status,                       #  On Time / Late
#         attendance_status=Attendance.ATT_PRESENT,  # new field for Present / Absent
#         date=today,
#         check_in_time=timezone.now()
#     )

#     return Response({
#         'success': True,
#         'attendance': {
#             'sn': attendance.id,
#             'date': attendance.date.strftime("%m/%d/%Y"),
#             'time': attendance.check_in_time.strftime("%H:%M:%S %p"),
#             'ip': attendance.ip_address,
#             'status': attendance.status,               # On Time / Late
#             'attendance_status': attendance.attendance_status  # Present / Absent
#         }
#     }) 
@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attendance_api(request):
    user = request.user
    today = date.today()
    now = timezone.now()
    client_ip = get_client_ip(request)

    # Already marked
    if Attendance.objects.filter(user=user, date=today).exists():
        return Response(
            {'success': False, 'error': 'Attendance already marked today.'},
            status=400
        )


    #  Outside time window → ABSENT
    if not is_within_time_window():
        attendance = Attendance.objects.create(
            user=user,
            date=today,
            attendance_status=Attendance.ATT_ABSENT,
            status="Absent",
            check_in_time=now,
            ip_address=client_ip
        )
        return Response(
            {'success': False, 'error': 'Attendance window closed. You have been marked absent.'},
            status=403
        )
    
    if is_holiday(today):
        return Response({"success": False, "error": "Attendance cannot be marked on a holiday." }, status=403)

    # Wrong IP → ALERT ONLY (NO ABSENT)
    if client_ip not in settings.ALLOWED_ATTENDANCE_IPS:
        return Response(
            {
                'success': False,
                'error': 'Attendance can only be marked from the office network.'
            },
            status=403
        )

    # PRESENT
    on_time_limit = now.replace(hour=9, minute=30, second=0, microsecond=0)
    status = "On Time" if now <= on_time_limit else "Late"

    attendance = Attendance.objects.create(
        user=user,
        date=today,
        ip_address=client_ip,
        check_in_time=now,
        status=status,
        attendance_status=Attendance.ATT_PRESENT
    )

    return Response({
        'success': True,
        'attendance': {
            'sn': attendance.id,
            'date': attendance.date.strftime("%m/%d/%Y"),
            'time': attendance.check_in_time.strftime("%I:%M:%S %p"),
            'ip': attendance.ip_address,
            'status': attendance.status,
            'attendance_status': attendance.attendance_status
        }
    }, status=201)

# user attendence history
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def attendance_history_api(request):
    user = request.user
    records = user.attendances.order_by('-date').all()  # latest first

    data = [
        {
            'sn': idx + 1,
            'date': att.date.strftime("%m/%d/%Y"),
            'time': att.check_in_time.strftime("%H:%M:%S %p"),
            'ip': att.ip_address,
            'attendance_status':att.attendance_status,
            'status': att.status
        }
        for idx, att in enumerate(records)
    ]

    return Response({'success': True, 'records': data})
#------------------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def attendance_history(request):
#     user = request.user
#     records = Attendance.objects.filter(user=user).order_by('-date')  # latest first

#     data = [
#         {
#             'sn': idx + 1,
#             'id':id,
#             'date': att.date.strftime("%m/%d/%Y"),
#             'time': att.check_in_time.strftime("%H:%M:%S %p"),
#             'ip': att.ip_address,
#             'status': att.status
#         }
#         for idx, att in enumerate(records)
#     ]
#     return Response({'success': True, 'records': data})

#-----------------------------------------------
#specific user attendence filter according to user id
from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import Adduser
from .models import Adduser

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # or add IsAdminUser for security
def attendance_by_user(request, user_id):
    # Get the user object (404 if not found)
    user = get_object_or_404(Adduser, id=user_id)

    # Filter attendance for that user
    records = Attendance.objects.filter(user=user).order_by('-date')

    data = [
        {
            'sn': idx + 1,
            'date': att.date.strftime("%m/%d/%Y"),
            'time': att.check_in_time.strftime("%H:%M:%S %p"),
            'ip': att.ip_address,
            'attendance_status':att.attendance_status,
            'status': att.status
        }
        for idx, att in enumerate(records)
    ]
    
    return Response({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        },
        'records': data
    })




# user attendence history for admin, for listing all
@api_view(['GET'])
@permission_classes([IsAdminUser, IsAuthenticated])
# @permission_classes(IsAdminUser)  # Only admins can access
def all_attendance_api(request):
    """
    API to list attendance of all users, latest first.
    """
    records = Attendance.objects.select_related('user').order_by('-date', '-check_in_time')
    
    data = [
        {
            'sn': idx + 1,
            'id':att.id,
            'username': f"{att.user.username} {att.user.get_full_name()}",
            'date': att.date.strftime("%m/%d/%Y"),
            'time': att.check_in_time.strftime("%H:%M:%S %p"),
            'ip': att.ip_address,
            'attendance_status':att.attendance_status,
            'status': att.status
        }
        for idx, att in enumerate(records)
    ]
    return Response({'success': True, 'records': data})
 
#--------------------------------------------------#

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
    role = data.get("role", "")
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
    user.role = role
    user.contact_number=contact_number
    user.address=address
    user.employee_id=employee_id
    user.is_staff = False
    user.is_superuser = False
    user.is_active = True
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
#----------------------------------------
# add profile picture of user
from cloudinary.uploader import destroy
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

    if 'is_active' in data:
        user.is_active = data['is_active']

    if 'email' in data:
        user.email = data['email']

    if 'contact_number' in data:
        user.contact_number = data['contact_number']

    if 'role' in data:
        if data['role'] in dict(Adduser.ROLE_CHOICES):
            user.role = data['role']
        else:
            return JsonResponse({'success': False, 'error': 'Invalid role'}, status=400)

    user.save()

    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_active': user.is_active,
            'role': user.role,
            'contact_number': user.contact_number,
        }
    })

# all user list 
@csrf_exempt
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def user_list_api(request):
    # Get all users and their status
    users = Adduser.objects.all().values('id', 'role', 'username', 'email', 'is_active','contact_number','address','employee_id')
    active_users = [u for u in users if u['is_active']]
    disabled_users = [u for u in users if not u['is_active']]

    return Response({
        'success': True,
        'active_users': active_users,
        'disabled_users': disabled_users
    }, status=status.HTTP_200_OK)



# deleting the user 
# @csrf_exempt
# def user_delete_api(request, user_id):
#     if request.method != 'DELETE':
#         return JsonResponse({'success': False, 'error': 'DELETE request required'}, status=400)

#     try:
#         user = Adduser.objects.get(id=user_id)
#     except Adduser.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

#     user.is_disabled=True
#     user.save()

#     return JsonResponse({'success': True, 'message': 'User deleted successfully'})



# only disable the user 
@csrf_exempt
def user_delete_api(request, user_id):
    if request.method != 'POST':  # POST for disabling
        return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)

    try:
        user = Adduser.objects.get(id=user_id)
        user.is_active = False
        user.save()
        return JsonResponse({'success': True, 'message': 'User disabled successfully'})
    except Adduser.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'}, status=404)

#-----------------------------------------------------------
# subbmiting the leave 
#-----------------------------------------------------------

from rest_framework.decorators import api_view, permission_classes, parser_classes
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def submit_leave_api(request):
    user = request.user
    # full_name = request.data.get('full_name')
    leave_type = request.data.get('leave_type')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    reason = request.data.get('reason')
    alternate_contact = request.data.get('alternate_contact')
    document = request.FILES.get('document')

    if not leave_type  or not start_date or not end_date or not reason:
        return Response({'success': False, 'message': 'All fields are required.'}, status=400)

    try:
        # Let CloudinaryField handle the upload automatically
        leave = LeaveRequest.objects.create(
            employee=user,
            full_name=user.Full_Name,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            alternate_contact=alternate_contact,
            email=user.email,
            leave_type=leave_type,
            document=document  # CloudinaryField handles this
        )
        
        # Get URL after save
        doc_url = leave.document.url if leave.document else None
        doc_filename = str(leave.document).split('/')[-1] if leave.document else None
        
        return Response({
            'success': True,
            'message': 'Leave request submitted successfully!',
            'leave': {
                'id': leave.id,
                'employee': leave.full_name,
                'email': leave.email,
                'start_date': leave.start_date,
                'end_date': leave.end_date,
                'reason': leave.reason,
                'alternate_contact': leave.alternate_contact,
                'leave_type': leave.leave_type,
                'status': leave.status,
                'document_url': doc_url,
                'document_filename': doc_filename
            }
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Upload failed: {str(e)}'
        }, status=500)
    # doc_url = leave.document.url if leave.document else None
    # doc_filename = str(leave.document).split('/')[-1] if leave.document else None

    # # Return API response
    # return Response({
    #     'success': True,
    #     'message': 'Leave request submitted successfully!',
    #     'leave': {
    #         'id': leave.id, 
    #         'employee': leave.full_name,
    #         'email': leave.email,
    #         'leave_type': leave.leave_type,
    #         'status': leave.status,
    #         'document_url': doc_url,  # FIXED: Use .url for full URL
    #         'document_filename': doc_filename  # Bonus: filename
    #     }
    # })

# from rest_framework.parsers import MultiPartParser, FormParser
# from rest_framework.decorators import api_view, permission_classes, parser_classes
# import cloudinary.uploader
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser])
# def submit_leave_api(request):
#     user = request.user
#     full_name=request.data.get('full_name')
#     leave_type = request.data.get('leave_type')
#     # date = request.data.get('start_date')
#     document = request.FILES.get('document')

#     # Validate
#     if not leave_type or not full_name or not document:
#         return Response({'success': False, 'message': 'All fields are required.'}, status=400)

#     # Upload directly to Cloudinary
    
#     upload_result = cloudinary.uploader.upload(
#         document,
#         resource_type='raw',
#         access_mode="public",
#         folder='leave_docs'
        
#     )

#     leave = LeaveRequest.objects.create(
#         employee=user,
#         full_name=full_name,
#         email=user.email,
#         leave_type=leave_type,
#         document=upload_result['leave_docs/']  # store Cloudinary public_id
#     )
    
    # Notify admin (optional)
    # try:
    #     send_mail(
    #         subject=f"New Leave Request from {leave.full_name}",
    #         message=f"Leave request submitted by {leave.full_name} ({leave.email}). Please review.",
    #         from_email=leave.email,
    #         recipient_list=[settings.ADMIN_EMAIL]
    #     )
    # except:
    #     # Ignore email errors for now
    #     pass

    # Return API response
    # return Response({
    #     'success': True,
    #     'message': 'Leave request submitted successfully!',
    #     'leave': {
    #         'id': leave.id, 
    #         'employee': leave.full_name,
    #         'email': leave.email,
    #         'leave_type': leave.leave_type,
    #         'status': leave.status,
    #         'document_url': leave.document
    #     }
    # })
#-----------------------------------------------------------
# listing all the user leaves applications 
# user leave ,List leave requests,specific one user by filtering id 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_all_leaves_api(request):
    user = request.user

    # Only admin/staff can access
    if not user.is_staff:
        return Response(
            {"success": False, "error": "Permission denied"},
            status=403
        )

    leaves = LeaveRequest.objects.select_related('employee').order_by('-id')

    data = []
    for leave in leaves:
        # Since document is now a URLField, just use it directly
        doc_url = None
        filename = None
        
        # Extract filename from URL
        if leave.document:
            doc_url = leave.document.url 
            filename = leave.document.public_id.split('/')[-1]

        data.append({
            "id": leave.id,
            "employee": {
                "id": leave.employee.id,
                "name": getattr(leave.employee, "Full_Name", leave.employee.username),
                "email": leave.employee.email,
            },
            "full_name": leave.full_name,
            "email": leave.email,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "reason": leave.reason,
            "alternate_contact": leave.alternate_contact,
            "leave_type": leave.leave_type,
            "status": leave.status,
            "reject_reason": leave.reject_reason,
            "document_url": doc_url,
            "document_filename": filename,
            "submitted_at": leave.created_at.strftime("%Y-%m-%d %H:%M:%S") if leave.created_at else None
        })

    return Response({
        "success": True,
        "applications": data
    })
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_leaves_api(request):
    """
    Admin API: 
    - List all leave requests
    - List leaves of a specific user (?user_id=<id>)
    - Get a single leave by leave ID (?leave_id=<id>)
    """
    leave_id = request.query_params.get('leave_id')
    user_id = request.query_params.get('user_id')

    leaves = LeaveRequest.objects.select_related('employee').order_by('-id')

    if leave_id:
        try:
            leave_id = int(leave_id)
            leaves = leaves.filter(id=leave_id)
        except ValueError:
            return Response({"success": False, "error": "Invalid leave_id"}, status=status.HTTP_400_BAD_REQUEST)

    if user_id:
        try:
            user_id = int(user_id)
            leaves = leaves.filter(employee__id=user_id)
        except ValueError:
            return Response({"success": False, "error": "Invalid user_id"}, status=status.HTTP_400_BAD_REQUEST)

    if not leaves.exists():
        return Response({"success": False, "error": "No leave requests found"}, status=status.HTTP_404_NOT_FOUND)

    data = []
    for leave in leaves:
        doc_url = leave.document.url if leave.document else None

        data.append({
            "id": leave.id,
            "employee": {
                "id": leave.employee.id,
                "name": getattr(leave.employee, "Full_Name", leave.employee.username),
                "email": leave.employee.email
            },
            "leave_type": leave.leave_type,
            "status": leave.status,
            "start_date": leave.start_date,
            "end_date": leave.end_date,
            "reason": leave.reason,
            "alternate_contact": leave.alternate_contact,
            "reject_reason": leave.reject_reason,
            "document_url": doc_url,
            "submitted_at": leave.created_at.strftime("%Y-%m-%d %H:%M:%S") if leave.created_at else None

        })

    # If leave_id is provided, return a single object instead of a list
    if leave_id:
        return Response({"success": True, "leave": data[0]})

    return Response({"success": True, "applications": data})


#------------------------------------------
#leave request approve and reject by adimn
#------------------------------------------


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_action_api(request, leave_id):
    # Only admin/staff can approve/reject
    if not request.user.is_staff:
        return Response({'success': False, 'message': 'Permission denied.'}, status=403)

    action = request.data.get('action')  # expected 'approve' or 'reject'
    reject_reason = request.data.get('reject_reason', '')

    if action not in ['approve', 'reject']:
        return Response({'success': False, 'message': 'Invalid action.'}, status=400)

    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        return Response({'success': False, 'message': 'Leave not found.'}, status=404)

     # =========================
    # APPROVE
    # =========================
    if action == 'approve':
        leave.status = 'approved'
        leave.reject_reason = None
        email_message = (
            f"Hello {leave.full_name},\n\n"
            f"Your leave request ({leave.leave_type}) has been approved.\n\n"
            f"Regards,\nHR Team"
        )

    # =========================
    # REJECT
    else:
        if not reject_reason:
            return Response({'success': False, 'message': 'Reject reason is required.'}, status=400)
        leave.status = 'rejected'
        leave.reject_reason = reject_reason
        email_message = (
            f"Hello {leave.full_name},\n\n"
            f"Your leave request ({leave.leave_type}) has been rejected.\n\n"
            f"Reason:\n{reject_reason}\n\n"
            f"If you have questions, please contact HR.\n\n"
            f"Regards,\nHR Team"
        )

    # Update leave status
    leave.save()

    # Notify user via email
    try:
        send_mail(
            subject=f"Leave Request {leave.status.capitalize()}",
            message=email_message,
            from_email=settings.DEFAULT_FROM_EMAIL,  # will use DEFAULT_FROM_EMAIL
            recipient_list=[leave.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send email to {leave.email}: {e}")

    return Response({
        'success': True,
        'status':leave.status,
        'message': f'Leave {leave.status} successfully.'
    })  

# only admin sees the details of the 
from django.db.models import Count, Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def present_absent_summary_api(request):
    user = request.user
    if not user.is_staff:
        return Response(
            {"success": False, "error": "Permission denied"},
            status=403
        )

    summary = (
        Attendance.objects
        .values('user__id', 'user__username', 'user__email')
        .annotate(
            present_days=Count('id', filter=Q(status='Present')),
            absent_days=Count('id', filter=Q(status='Absent')),
            total_days=Count('id')
        )
    )

    return Response({
        "success": True,
        "data": summary
    })


# making the view for the only one user details of the user 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Attendance

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_attendance_summary_api(request):
    user = request.user

    print("AUTH USER ID:", user.id)
    print("AUTH USER EMAIL:", user.email)

    present_days = Attendance.objects.filter(
        user=user, attendance_status='Present'
    ).count()

    absent_days = Attendance.objects.filter(
        user=user, attendance_status='Absent'
    ).count()

    return Response({
        "success": True,
        "present_days": present_days,
        "absent_days": absent_days,
        "total_days": present_days + absent_days
    })


#-----------------------------------------------------------#
# inserting holidays by admin
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def holiday_create_api(request):
    user = request.user
    if not user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    description = request.data.get('description')

    if not start_date_str or not description:
        return Response({"success": False, "error": "start_date and description are required"}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date < start_date:
                return Response({"success": False, "error": "end_date cannot be before start_date"}, status=400)
    except ValueError:
        return Response({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

    holiday = Holiday.objects.create(start_date=start_date, end_date=end_date, description=description)

    return Response({
        "success": True,
        "holiday": {
            "id": holiday.id,
            "start_date": holiday.start_date.strftime("%Y-%m-%d"),
            "end_date": holiday.end_date.strftime("%Y-%m-%d") if holiday.end_date else None,
            "description": holiday.description
        }
    }, status=201)

#-----------------------------------------------------------#
# Getting all the holidays
from .models import Holiday
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def holiday_list_api(request):
    user = request.user
    if not user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    holidays = Holiday.objects.all().order_by('-start_date')

    data = []
    for holiday in holidays:
        data.append({
            "id": holiday.id,
            "start_date": holiday.start_date.strftime("%Y-%m-%d"),
            "end_date": holiday.end_date.strftime("%Y-%m-%d") if holiday.end_date else None,
            "description": holiday.description
        })

    return Response({
        "success": True,
        "holidays": data
    })

#-----------------------------------------------------------#
# delete holiday by admin
from datetime import timedelta, datetime

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def holiday_delete_api(request):
    user = request.user
    if not user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    holiday_id = request.data.get("holiday_id")
    date_str = request.data.get("date")

    if not holiday_id or not date_str:
        return Response({"success": False, "error": "holiday_id and date are required"}, status=400)

    try:
        delete_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        holiday = Holiday.objects.get(id=holiday_id)
    except (ValueError, Holiday.DoesNotExist):
        return Response({"success": False, "error": "Invalid data"}, status=400)

    start = holiday.start_date
    end = holiday.end_date or holiday.start_date

    if delete_date < start or delete_date > end:
        return Response({"success": False, "error": "Date not in holiday range"}, status=400)

    # CASE 1: single-day holiday
    if start == end == delete_date:
        holiday.delete()

    # CASE 2: deleting start date
    elif delete_date == start:
        holiday.start_date = start + timedelta(days=1)
        holiday.save()

    # CASE 3: deleting end date
    elif delete_date == end:
        holiday.end_date = end - timedelta(days=1)
        holiday.save()

    # CASE 4: deleting middle date → split
    else:
        Holiday.objects.create(
            start_date=start,
            end_date=delete_date - timedelta(days=1),
            description=holiday.description
        )
        holiday.start_date = delete_date + timedelta(days=1)
        holiday.save()

    return Response({"success": True, "message": "Holiday date removed successfully"})
