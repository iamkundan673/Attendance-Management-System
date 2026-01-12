from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response    
from .models import LeaveRequest
from django.contrib.auth import get_user_model
from ams.services import notify
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
# Create your views here.

#-----------------------------------------------------------
# subbmiting the leave 
#-----------------------------------------------------------
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
        #get notify by admin
        User = get_user_model()
        admins = User.objects.filter(is_staff=True, is_active=True)

        for admin in admins:
            notify(
                user=admin,
                title="New Leave Request",
                message=f"{user.Full_Name} submitted a {leave_type} leave "
                    f"from {start_date} to {end_date}.",
                type="leave"
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
            {"success": False, "error": "Permission denied"},status=403
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
        return Response(status=204)

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

        #  USER NOTIFICATION
        notify(
            user=leave.employee,
            title="Leave Approved",
            message=f"Your {leave.leave_type} leave has been approved.",
            type="leave"
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
         # USER NOTIFICATION
        notify(
            user=leave.employee,
            title="Leave Rejected",
            message=f"Your {leave.leave_type} leave was rejected. Reason: {reject_reason}",
            type="leave"
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


