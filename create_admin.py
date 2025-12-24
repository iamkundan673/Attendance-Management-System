# create_admin.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Change these to your desired admin credentials
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@.com"
ADMIN_PASSWORD = "123456789"

if not User.objects.filter(username=ADMIN_USERNAME).exists():
    User.objects.create_superuser(
        username=ADMIN_USERNAME,
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD
    )
    print(f"Superuser {ADMIN_USERNAME} created successfully.")
else:
    print(f"Superuser {ADMIN_USERNAME} already exists.")
