from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime, time
from django.shortcuts import get_object_or_404
from ams.models import Attendance,User as Adduser
from ams.models.User import  Adduser
from django.conf import settings
from ams.utils import get_client_ip, is_holiday
from rest_framework.permissions import IsAdminUser
from django.http import JsonResponse
from ip.utils import get_client_ip, is_ip_allowed,distance_meters
from django.db.models import Count, Q

import ipaddress

def is_ip_allowed(client_ip, cidr_range):
    try:
        ip = ipaddress.ip_address(client_ip)
        network = ipaddress.ip_network(cidr_range, strict=False)
        return ip in network
    except ValueError:
        return False


#---mark attendence ho
def is_within_time_window():
    now = datetime.now().time()  # current server time
    return settings.ATTENDANCE_START_TIME <= now <= settings.ATTENDANCE_END_TIME


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def attendance_api(request):
    user = request.user
    client_ip = get_client_ip(request)

    # IP range check
    if not is_ip_allowed(client_ip, settings.ALLOWED_PUBLIC_IP_RANGE):
        return Response({
            'success': False,
            'error': 'Attendance can only be marked from the office network'
        }, status=403)

    # Time window check
    now = datetime.now().time()
    if not (settings.ATTENDANCE_START_TIME <= now <= settings.ATTENDANCE_END_TIME):
        return Response({
            'success': False,
            'error': f'Attendance can only be marked between {settings.ATTENDANCE_START_TIME.strftime("%H:%M")} and {settings.ATTENDANCE_END_TIME.strftime("%H:%M")}'
        }, status=403)

    today = date.today()

    #  Holiday check
    if is_holiday(today):
        return Response({
            "success": False,
            "error": "Attendance cannot be marked on a holiday."
        }, status=403)

    #  Already marked check
    if Attendance.objects.filter(user=user, date=today).exists():
        return Response({'success': False, 'error': 'Attendance already marked today.'})

    #  GPS / Meter range check (optional: requires frontend to send lat/lon)
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    if latitude and longitude:
        try:
            lat = float(latitude)
            lon = float(longitude)
            office_lat = settings.OFFICE_LATITUDE
            office_lon = settings.OFFICE_LONGITUDE
            distance = distance_meters(lat, lon, office_lat, office_lon)

            if distance > settings.ATTENDANCE_RADIUS_METERS:
                return Response({
                    "success": False,
                    "error": f"Attendance can only be marked within {settings.ATTENDANCE_RADIUS_METERS} meters of office. You are {int(distance)} meters away."
                }, status=403)

        except ValueError:
            return Response({
                "success": False,
                "error": "Invalid latitude or longitude format."
            }, status=400)

    #  Determine punctuality
    status = "On Time" if now <= datetime.strptime("09:30:00", "%H:%M:%S").time() else "Late"

    #  Save attendance
    attendance = Attendance.objects.create(
        user=user,
        ip_address=client_ip,
        status=status,                       
        attendance_status=Attendance.ATT_PRESENT,  
        date=today,
        check_in_time=timezone.now()
    )

    #  Return response
    return Response({
        'success': True,
        'attendance': {
            'sn': attendance.id,
            'date': attendance.date.strftime("%m/%d/%Y"),
            'time': attendance.check_in_time.strftime("%H:%M:%S %p"),
            'ip': attendance.ip_address,
            'status': attendance.status,
            'attendance_status': attendance.attendance_status
        }
    })


# only admin sees the details of the 
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

#------------------------------------
# auto mark attendence absent function
#-------------------------------------
def auto_mark_absent(request, secret_key):
    if secret_key != settings.AUTO_MARK_SECRET:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    today = date.today()
    now_time = datetime.now().time()
    # Skip holidays & weekends
    if is_holiday(today) or today.weekday() == 5:
        return JsonResponse({'status': 'No attendance update today (holiday/weekend).'})

    # Define attendance timings
    start_attendance_time = time(10, 00)  # 10:00 AM
    end_attendance_time = time(12, 00)    # 11:00 AM

    # Case 1: Before 10:00 AM → no attendance allowed
    if now_time < start_attendance_time:
        return JsonResponse({'status': 'Attendance not open yet. Please come after 10:00 AM.'})

    # Case 2: Between 10:00 AM and 11:00 AM → attendance open
    if start_attendance_time <= now_time < end_attendance_time:
        return JsonResponse({'status': 'Attendance window open. Users can mark attendance now.'})

    # Case 3: After 11:00 AM → auto-mark absent
    if now_time >= end_attendance_time:
        users = Adduser.objects.filter(is_active=True)
        updated_count = 0

        for user in users:
            attendance = Attendance.objects.filter(user=user, date=today).first()

            # Skip if already marked present
            if attendance and attendance.attendance_status == Attendance.ATT_PRESENT:
                continue

            # Create absent record if not exists
            if not attendance:
                Attendance.objects.create(
                    user=user,
                    date=today,
                    attendance_status=Attendance.ATT_ABSENT,
                    status="Absent",
                    ip_address=None
                )
                updated_count += 1

        return JsonResponse({
            'status': 'Auto-mark absent completed',
            'users_marked_absent': updated_count
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
#-----------------------------------------------
#specific user attendence filter according to user id

# from django.contrib.auth.models import Adduser
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
            'time': att.check_in_time.strftime("%H:%M:%S %p") if att.check_in_time else "-",
            'ip': att.ip_address if att.ip_address else "-",
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
 