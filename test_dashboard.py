import os
import django

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.hr.views import DashboardView
from apps.hr.models import InternProfile

User = get_user_model()

def test():
    print("--- STARTING DASHBOARD TEST ---")
    
    # 1. Get our Genesis User (The Super Admin)
    try:
        user = User.objects.get(role='SUP')
        print(f"1. Found User: {user.display_id}")
    except User.DoesNotExist:
        print("CRITICAL: Genesis Admin not found. Run 'init_genesis' first.")
        return

    # 2. Create a Fake Profile for the Admin (So the dashboard doesn't crash)
    # Use get_or_create so we don't duplicate it if you run this twice
    profile, created = InternProfile.objects.get_or_create(
        user=user,
        defaults={
            "designation": "Super Admin",
            "department": "Management",
            "phone_number": "9999999999"
        }
    )
    if created:
        print("2. Created temporary profile for Admin.")
    else:
        print("2. Profile already exists.")

    # 3. Simulate the API Call
    factory = APIRequestFactory()
    request = factory.get('/api/v1/hr/dashboard/')
    force_authenticate(request, user=user) # Bypass password check for test
    
    view = DashboardView.as_view()
    response = view(request)
    
    # 4. Print Result
    print("\n--- API RESPONSE (JSON) ---")
    print(response.data)
    print("---------------------------")

if __name__ == "__main__":
    test()