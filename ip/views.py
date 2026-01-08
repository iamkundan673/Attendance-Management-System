from django.shortcuts import render
from .models import OfficeIP
from rest_framework.response import Response
from rest_framework import status
# Create your views here.
# ip 
# retrieve client's public ip address
def get_user_ip_address(request):
    try:
        # 1. Get user IP
        user_ip = request.META.get('HTTP_X_FORWARDED_FOR')
        if user_ip:
            user_ip = user_ip.split(',')[0].strip()
        else:
            user_ip = request.META.get('REMOTE_ADDR')

        # Remove IPv6 prefix
        clean_ip = user_ip.replace("::ffff:", "")

        # 2. Fetch allowed IPs
        setting = OfficeIP.objects.first()
        if setting is None:
            return Response({
                "success": False,
                "message": "Allowed IP list not configured."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 3. Check if IP is allowed
        if clean_ip not in setting.ips:
            return Response({
                "success": False,
                "message": "You can mark attendance only from office IP."
            }, status=status.HTTP_403_FORBIDDEN)

        # 4. Allowed → continue marking attendance
        return Response({
            "success": True,
            "message": "Attendance marked successfully!"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)