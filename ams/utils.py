# ams/utils.py

# Define allowed LAN prefixes for your office network
ALLOWED_LAN_RANGES = [
    "192.168.1.",  # office LAN subnet
]


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

def is_in_office_network(ip):
    """
    Check if the given IP starts with one of the allowed LAN prefixes
    """
    return any(ip.startswith(prefix) for prefix in ALLOWED_LAN_RANGES)
