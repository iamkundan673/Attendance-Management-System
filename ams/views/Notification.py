from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ams.models import Notification
from ams.serializer import NotificationSerializer
from django.shortcuts import get_object_or_404


#notification view
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, id):
    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    if notification.is_read:
        return Response({
            "success": True,
            "message": "Notification already marked as read"
        })

    notification.is_read = True
    notification.save()

    return Response({
        "success": True,
        "message": "Notification marked as read"
    })
