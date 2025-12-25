# ams/utils.py

# Define allowed LAN prefixes for your office network
def get_client_ip(request):
    """
    Get client IP from request headers
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Sometimes multiple IPs are listed
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

from datetime import date
from .models import Holiday

def is_holiday(check_date: date) -> bool:
    """
    Returns True if the given date is a holiday.
    Works for both single-day and multi-day holidays.
    """
    # Check single-day holidays or multi-day ranges
    return Holiday.objects.filter(
        start_date__lte=check_date,
        end_date__gte=check_date
    ).exists() or Holiday.objects.filter(
        start_date=check_date,
        end_date__isnull=True
    ).exists()
