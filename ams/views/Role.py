from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from myproject.ams.models import Role



#api for the role creation
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_role_api(request):
    role_name = request.data.get("role")

    if not role_name:
        return Response({"detail": "Role name is required"}, status=400)

    # Normalize the input (e.g. 'frontend ' -> 'Frontend')
    role_name = role_name.strip().title()

    role, created = Role.objects.get_or_create(name=role_name)

    return Response({
        "success": True,
        "message": "Role created" if created else "Role already exists",
        "role": role.name
    }, status=201 if created else 200)


#getiing all the roles
@api_view(["GET"])
def get_roles_api(request):
    roles = Role.objects.all().values("id", "name")
    return Response({"success": True, "roles": list(roles)}, status=200)



#update or edit the role 
@api_view(["PUT"])
@permission_classes([IsAdminUser])   # optional, remove if frontend test only
def edit_role_api(request, role_id):
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response(
            {"success": False, "error": "Role not found"},
            status=404
        )

    new_name = request.data.get("role")
    if not new_name:
        return Response(
            {"success": False, "error": "New role name is required"},
            status=400
        )

    new_name = new_name.strip().title()

    # Avoid renaming conflict
    if Role.objects.exclude(id=role_id).filter(name=new_name).exists():
        return Response(
            {"success": False, "error": "Role name already exists"},
            status=409
        )

    role.name = new_name
    role.save()

    return Response({
        "success": True,
        "message": "Role updated successfully",
        "role": role.name
    }, status=200)
