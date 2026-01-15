
from rest_framework_simplejwt.views import TokenObtainPairView
from ams.serializer import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated 
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#logout api
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_api(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()   # kill refresh token

        return Response({"success": True, "message": "Logged out successfully"})
    except Exception:
        return Response({"success": False, "message": "Invalid token"}, status=400)