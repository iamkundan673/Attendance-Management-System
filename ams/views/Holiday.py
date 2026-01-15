from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny 
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from datetime import datetime
from ams.models import Holiday
from ams.services import notify
from datetime import timedelta

#-----------------------------------------------------------
# inserting holidays by admin
#-----------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def holiday_create_api(request):
    user = request.user
    if not user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    start_date_str = request.data.get('start_date')
    end_date_str = request.data.get('end_date')
    description = request.data.get('description')

    if not start_date_str or not description:
        return Response({"success": False, "error": "start_date and description are required"}, status=400)

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = None
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            if end_date < start_date:
                return Response({"success": False, "error": "end_date cannot be before start_date"}, status=400)
    except ValueError:
        return Response({"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

    holiday = Holiday.objects.create(start_date=start_date, end_date=end_date, description=description)
    
     # Notify all active users
    User = get_user_model()
    users = User.objects.filter(is_active=True,is_staff=False)

    date_text = (
        f"{start_date} to {end_date}" if end_date else f"{start_date}"
    )

    for u in users:
        notify(
            user=u,
            title="New Holiday",
            message=f"{description} ({date_text})",
            type="holiday"
        )

    return Response({
        "success": True,
        "holiday": {
            "id": holiday.id,
            "start_date": holiday.start_date.strftime("%Y-%m-%d"),
            "end_date": holiday.end_date.strftime("%Y-%m-%d") if holiday.end_date else None,
            "description": holiday.description
        }
    }, status=201)

#-----------------------------------------------------------#
# Getting all the holidays
@api_view(['GET'])
@permission_classes([AllowAny])
def holiday_list_api(request):
    holidays = Holiday.objects.all().order_by('-start_date')

    data = []
    for holiday in holidays:
        data.append({
            "id": holiday.id,
            "start_date": holiday.start_date.strftime("%Y-%m-%d"),
            "end_date": holiday.end_date.strftime("%Y-%m-%d") if holiday.end_date else None,
            "description": holiday.description
        })

    return Response({
        "success": True,
        "holidays": data
    })


#-----------------------------------------------------------#
# delete holiday by admin
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def holiday_delete_api(request):
    user = request.user
    if not user.is_staff:
        return Response({"success": False, "error": "Permission denied"}, status=403)

    holiday_id = request.data.get("holiday_id")
    date_str = request.data.get("date")  # you can also allow list of dates if needed

    if not holiday_id or not date_str:
        return Response({"success": False, "error": "holiday_id and date are required"}, status=400)

    try:
        delete_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        holiday = Holiday.objects.get(id=holiday_id)
    except (ValueError, Holiday.DoesNotExist):
        return Response({"success": False, "error": "Invalid data"}, status=400)

    start = holiday.start_date
    end = holiday.end_date or holiday.start_date
    changes = []

    if delete_date < start or delete_date > end:
        return Response({"success": False, "error": "Date not in holiday range"}, status=400)

    deleted_dates = []  # Collect all affected dates

    # CASE 1: single-day holiday
    if start == end == delete_date:
        deleted_dates.append(delete_date)
        holiday.delete()
        changes.append("Holiday deleted")
    # CASE 2: deleting start date
    elif delete_date == start:
        deleted_dates.append(start)
        holiday.start_date = start + timedelta(days=1)
        holiday.save()
        changes.append("Holiday start date updated")
    # CASE 3: deleting end date
    elif delete_date == end:
        deleted_dates.append(end)
        holiday.end_date = end - timedelta(days=1)
        holiday.save()
        changes.append("Holiday end date updated")
    # CASE 4: deleting middle date → split
    else:
        # All dates before delete_date
        Holiday.objects.create(
            start_date=start,
            end_date=delete_date - timedelta(days=1),
            description=holiday.description
        )
        # Update current holiday to start after deleted date
        holiday.start_date = delete_date + timedelta(days=1)
        holiday.save()
        deleted_dates.append(delete_date)
        changes.append("Holiday split into two ranges")

    # ------------------------------------------------------
    # Notify all active non-admin users ONE TIME
    # ------------------------------------------------------
    if deleted_dates:
        User = get_user_model()
        users = User.objects.filter(is_active=True, is_staff=False)  # only normal users
        # Convert deleted_dates to readable string
        deleted_dates_text = ", ".join([d.strftime("%Y-%m-%d") for d in deleted_dates])

        for u in users:
            notify(
                user=u,
                title="Holiday Updated",
                message=f"{holiday.description} has been removed/updated for the following date(s): {deleted_dates_text}.",
                type="holiday"
            )

    return Response({"success": True, "message": "Holiday date removed successfully"})


