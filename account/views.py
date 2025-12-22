# ams/views.py
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes


# admin login
@api_view(['POST'])
# @permission_classes([IsAdminUser])
def user_login_api(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '').strip()

    if not username or not password:
        return Response({"detail": "Username and password required"}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)

    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "is_staff": user.is_staff,
        "username": user.username
    })


# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAuthenticated
# from .models import Adduser
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def create_user_api(request):
#     if not request.user.is_staff:
#         return Response({"detail": "Not allowed"}, status=403)

#     username = request.data.get("username")
#     email = request.data.get("email", "")
#     password = request.data.get("password")

#     if not username or not password:
#         return Response({"detail": "Username and password required"}, status=400)

#     if Adduser.objects.filter(username=username).exists():
#         return Response({"detail": "Username already exists"}, status=400)

#     user = Adduser.objects.create_user(
#         username=username,
#         email=email,
#         password=password,
#         is_staff=False,
#         is_superuser=False
#     )

#     return Response({
#         "id": user.id,
#         "username": user.username,
#         "email": user.email
#     })
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def admin_dashboard(request):
#     if not request.user.is_staff:
#         return Response({"detail": "Not allowed"}, status=403)

#     users = Adduser.objects.all().values('id', 'username', 'email', 'is_staff')
#     return Response({"users": list(users)})


# admin login and rejection
# @login_required
# def leave_list_admin(request):
#     if not request.user.is_staff:
#         return redirect('submit_leave')
#     leaves = LeaveRequest.objects.all().order_by('-created_at')
#     return render(request, 'leave_list_admin.html', {'leaves': leaves})

# @login_required
# def approve_leave(request, leave_id):
#     if not request.user.is_staff:
#         return redirect('submit_leave')
#     leave = LeaveRequest.objects.get(id=leave_id)
#     leave.status = 'approved'
#     leave.save()
#     send_mail(
#         subject='Leave Request Approved',
#         message=f"Your leave request ({leave.leave_type}) has been approved.",
#         from_email='admin@example.com',
#         recipient_list=[leave.email]
#     )
#     return redirect('leave_list_admin')

# @login_required
# def reject_leave(request, leave_id):
#     if not request.user.is_staff:
#         return redirect('submit_leave')
#     leave = LeaveRequest.objects.get(id=leave_id)
#     leave.status = 'rejected'
#     leave.save()
#     send_mail(
#         subject='Leave Request Rejected',
#         message=f"Your leave request ({leave.leave_type}) has been rejected.",
#         from_email='admin@example.com',
#         recipient_list=[leave.email]
#     )
#     return redirect('leave_list_admin')
