from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


