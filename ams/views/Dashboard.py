from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Attendence page ko lagi,user specific data haru 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def dashboard_api(request):
#     """
#     Return logged-in user info using JWT authentication, structured for frontend.
#     """
#     user = request.user  # DRF sets this from the JWT

#     return Response({
#         'user': {
#             'userId': user.id,       # matches frontend's userId field
#             'username': getattr(user, 'username', ''),  # matches frontend's name
#             'email': user.email,
#             'contactNumber': getattr(user, 'contact_number', ''),  # optional, if you have this field
#             'role': getattr(user, 'role', ''),  # optional, if you have a role field
#             'address': getattr(user, 'address', ''), 
#             'employee_id': getattr(user, 'employee_id', ''), 
            
#         },
#         'success': True
#     })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_api(request):
    user = request.user  # JWT Auth handles this
    
    # Safe role extraction
    role_data = None
    if getattr(user, "role", None) is not None:
        role_data = {
            "id": user.role.id,
            "name": user.role.name
        }

    # Safe profile pic
    profile_picture_url = ""
    if getattr(user, "profile_picture", None):
        try:
            profile_picture_url = user.profile_picture.url
        except:
            profile_picture_url = ""

    return Response({
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": getattr(user, "Full_Name", "") or "",
            "email": user.email,
            "contact_number": getattr(user, "contact_number", "") or "",
            "address": getattr(user, "address", "") or "",
            "employee_id": getattr(user, "employee_id", "") or "",
            "role": role_data,
            "profile_picture": profile_picture_url,
            "is_staff": user.is_staff,
        }
    }, status=200)

