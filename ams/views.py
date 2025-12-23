# Create your views here.
from rest_framework.decorators import api_view,permission_classes
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
from .utils import get_client_ip
from datetime import date, datetime
from django.conf import settings
import os
from rest_framework import status 
from .serializer import AdduserSerializer
#--------------------------
# user login 
#--------------------------
@api_view(['POST'])
def user_login_api(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not username or not password:
        return Response({'success': False, 'message': 'Username and password are required'}, status=400)

    try:
        user = Adduser.objects.get(username=username)
    except Adduser.DoesNotExist:
        return Response({'success': False, 'message': 'Invalid username or password'}, status=401)

    if not check_password(password, user.password):
        return Response({'success': False, 'message': 'Invalid username or password'}, status=401)

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
    user.password = make_password(password)
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
            'role': getattr(user, 'role', ''),  # optional, if you have a role field
            'employeeId': getattr(user, 'employeeId', ''),  # optional
            
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


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attendance_api(request):
    user = request.user
    client_ip = get_client_ip(request)

    if client_ip not in settings.ALLOWED_ATTENDANCE_IPS:
        return Response({'success': False, 'error': 'Attendence can only be marked form the office network'}, status=403)

    if not is_within_time_window():
        return Response({'success': False, 'error': 'Attendance can only be marked between 9:00 AM and 10:30 AM'}, status=403)
    
    # Check if already marked today
    today = date.today()
    if Attendance.objects.filter(user=user, date=today).exists():
        return Response({'success': False, 'error': 'Attendance already marked today.'})

    # Determine punctuality status based on check-in time
    current_time = datetime.now().time()
    status = "On Time" if current_time <= datetime.strptime("09:30:00", "%H:%M:%S").time() else "Late"

    # Save attendance (with new attendance_status field)
    attendance = Attendance.objects.create(
        user=user,
        ip_address=client_ip,
        status=status,                       #  On Time / Late
        attendance_status=Attendance.ATT_PRESENT,  # new field for Present / Absent
        date=today,
        check_in_time=timezone.now()
    )

    return Response({
        'success': True,
        'attendance': {
            'sn': attendance.id,
            'date': attendance.date.strftime("%m/%d/%Y"),
            'time': attendance.check_in_time.strftime("%H:%M:%S %p"),
            'ip': attendance.ip_address,
            'status': attendance.status,               # On Time / Late
            'attendance_status': attendance.attendance_status  # Present / Absent
        }
    }) 

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

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user_api(request): 
    # Only staff/admin can create users
    if not request.user.is_staff:
        return Response({"detail": "Only admin can create users"}, status=403)

    data = request.data

    Full_Name = data.get("fullname") or data.get("Full_Name")
    email = data.get("email")
    role = data.get("role", "")

    # Validate required fields
    if not email:
        return Response({"detail": "Email is required"}, status=400)

    if not Full_Name:
        return Response({"detail": "Fullname is required"}, status=400)

    # Auto-generate username from email
    username = email.split("@")[0]

    # Check duplicates
    if Adduser.objects.filter(username=username).exists():
        return Response({"detail": "Username already exists"}, status=400)

    if Adduser.objects.filter(email=email).exists():
        return Response({"detail": "Email already exists"}, status=400)

    # Generate temporary password
    temp_password = generate_temp_password()

    # Handle profile picture
    profile_picture = request.FILES.get('profile_picture', None)

    # Create user
    user = Adduser.objects.create(
        Full_Name=Full_Name,
        username=username,
        email=email,
        role=role,
        password=make_password(temp_password),
        profile_picture=profile_picture,
        is_staff=False,
        is_superuser=False
    )

    # Send email with temp password
    subject = "Your Account Login Details"
    message = f"""
Hello {Full_Name},

Your account has been created successfully.

Login Details:
------------------------
Username: {username}
Email: {email}
Temporary Password: {temp_password}

Please log in and change your password immediately.

Thanks,
The Team
"""

    try:
        send_mail(subject, message, 'kundanchapagain555@gmail.com', [email])
    except Exception as e:
        return Response({
            "detail": "User created but failed to send email.",
            "error": str(e)
        }, status=500)

    serializer = AdduserSerializer(user)
    return Response({
        "success": True,
        "message": "User created. Temporary password sent to email.",
        "user": serializer.data
    })

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
            'role': user.role
        }
    })

# all user list 
@csrf_exempt
@api_view(["GET"])
# @permission_classes([IsAuthenticated])
def user_list_api(request):
    # Get all users and their status
    users = Adduser.objects.all().values('id', 'role', 'username', 'email', 'is_active')
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_leave_api(request):
    user = request.user
    full_name=request.data.get('full_name')
    leave_type = request.data.get('leave_type')
    # date = request.data.get('start_date')
    document = request.FILES.get('document')

    # Validate
    if not leave_type or not full_name or not document:
        return Response({'success': False, 'message': 'All fields are required.'}, status=400)


    leave = LeaveRequest.objects.create(
        employee=user,
        full_name=full_name,
        email=user.email,
        leave_type=leave_type,
        document=document
    )
    
    # Notify admin (optional)
    try:
        send_mail(
            subject=f"New Leave Request from {leave.full_name}",
            message=f"Leave request submitted by {leave.full_name} ({leave.email}). Please review.",
            from_email=leave.email,
            recipient_list=[settings.ADMIN_EMAIL]
        )
    except:
        # Ignore email errors for now
        pass

    # Return API response
    return Response({
        'success': True,
        'message': 'Leave request submitted successfully!',
        'leave': {
            'id': leave.id, 
            'employee': leave.full_name,
            'email': leave.email,
            'leave_type': leave.leave_type,
            'status': leave.status,
            'document_url': request.build_absolute_uri(leave.document.url)
        }
    })


# listing all the user leaves applications 
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
        # Check if document exists before building URL
        doc_url = None
        if leave.document and os.path.exists(leave.document.path):
            doc_url = request.build_absolute_uri(leave.document.url)

        data.append({
            "id": leave.id,
            "employee": {
                "id": leave.employee.id,
                "name": getattr(leave.employee, "Full_Name", leave.employee.username),
                "leave_type":leave.leave_type,  # fallback to username
                "email": leave.employee.email,
            },
            "full_name": leave.full_name,
            "email": leave.email,
            "leave_type": leave.leave_type,
            "status": leave.status,
            "document_url": doc_url,
            "submitted_at": leave.created_at.strftime("%Y-%m-%d %H:%M:%S") if leave.created_at else None
        })

    return Response({
        "success": True,
        "applications": data
    })

# user leave ,List leave requests,specific one user by filtering id 
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     
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
        leaves = leaves.filter(id=leave_id)
    elif user_id:
        leaves = leaves.filter(employee__id=user_id)

    if not leaves.exists():
        return Response({"success": False, "error": "No leave requests found"}, status=status.HTTP_404_NOT_FOUND)

    data = []
    for leave in leaves:
        doc_url = None
        if leave.document and os.path.exists(leave.document.path):
            doc_url = request.build_absolute_uri(leave.document.url)

        data.append({
            "id": leave.id,
            "employee": {
                "id": leave.employee.id,
                "name": getattr(leave.employee, "Full_Name", leave.employee.username),
                "email": leave.employee.email
            },
            "leave_type": leave.leave_type,
            "status": leave.status,
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
    if action not in ['approve', 'reject']:
        return Response({'success': False, 'message': 'Invalid action.'}, status=400)

    try:
        leave = LeaveRequest.objects.get(id=leave_id)
    except LeaveRequest.DoesNotExist:
        return Response({'success': False, 'message': 'Leave not found.'}, status=404)

    # Update leave status
    leave.status = 'approved' if action == 'approve' else 'rejected'
    leave.save()

    # Notify user via email
    try:
        send_mail(
            subject=f"Leave Request {leave.status.capitalize()}",
            message=f"Hello {leave.full_name},\n\n"
                    f"Your leave request ({leave.leave_type}) has been {leave.status}.",
            from_email='kundanchapagain555@gmail.com',
            recipient_list=[leave.email],
            fail_silently=False,  # optional: will raise error if email fails
        )
    except Exception as e:
        print(f"Failed to send email to {leave.email}: {e}")

    return Response({
        'success': True,
        'status':leave.status,
        'message': f'Leave {leave.status} successfully.'
    })



# images -----store,
# leave details of the user

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
