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
