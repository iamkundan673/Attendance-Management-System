# ams/utils.py
import ipaddress

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

def is_ip_allowed(ip, allowed_range):
    try:
        network = ipaddress.ip_network(allowed_range)
        return ipaddress.ip_address(ip) in network
    except:
        return False
    
# ams/utils.py
import math

def distance_meters(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two lat/lon points in meters
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
    c = 2*math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance