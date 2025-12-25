from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import InternProfile
from .serializers import DashboardSerializer
from apps.common.notifications import NotificationService

# CROSS-MODULE IMPORT: Importing the logic from the Operations App
from apps.operations.services import get_dashboard_stats 

class DashboardView(APIView):
    """
    GET /api/v1/hr/dashboard/
    Fetches User Profile + Attendance Stats in one API call.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Fetch Profile Data (Top of Screen)
        try:
            profile = request.user.profile
        except InternProfile.DoesNotExist:
            return Response(
                {"error": "Intern Profile not found. Contact HR."}, 
                status=404
            )

        profile_data = DashboardSerializer(profile).data
        
        # 2. Fetch Chart Data (Bottom of Screen)
        # We call the service function from the Operations app
        chart_data = get_dashboard_stats(request.user)
        
        # 3. Merge and Return
        # This creates a single JSON object with everything the UI needs
        full_response = {
            "profile": profile_data,
            "analytics": chart_data
        }
        
        return Response(full_response)

from .serializers import DashboardSerializer, InternOnboardingSerializer # Import the new one

class OnboardInternView(APIView):
    """
    POST /api/v1/hr/onboard-intern/
    HR Admin creates a new Intern.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 1. Permission Check: Only HR or Super Admin
        if request.user.role not in ['SUP', 'ADM']: 
            # Ideally check department=='HR' too, but kept simple for now
            return Response({"error": "Unauthorized"}, status=403)

        serializer = InternOnboardingSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": f"Intern Onboarded: {user.display_id}",
                "default_password": "Welcome@123"
            }, status=201)
            
        serializer = InternOnboardingSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            
            # --- NOTIFICATION LOGIC ---
            # Fire and forget (don't block the API response if email fails)
            try:
                notifier = NotificationService()
                # The serializer sets a default password "Welcome@123"
                notifier.alert_onboarding(user, "Welcome@123") 
            except Exception as e:
                print(f"Notification Error: {e}")
            # -------------------------------------

            return Response({
                "message": f"Intern Onboarded: {user.display_id}",
                "default_password": "Welcome@123"
            }, status=201)

        return Response(serializer.errors, status=400)

import csv
import io
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.identity.permissions import IsDeptAdmin # Using our new RBAC permission
from .serializers import InternOnboardingSerializer

class BulkImportInternsView(APIView):
    """
    POST /api/v1/hr/bulk-import/
    Accepts a CSV file and creates Interns + Profiles.
    """
    permission_classes = [IsDeptAdmin]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "No file provided"}, status=400)

        # Decode CSV
        decoded_file = file_obj.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        success_count = 0
        errors = []

        for row in reader:
            # Map CSV columns to Serializer fields
            # Adjust these keys based on your specific CSV headers
            data = {
                "first_name": row.get('NAME', '').split(' ')[0],
                "last_name": row.get('NAME', '').split(' ')[-1],
                "email": f"{row.get('NAME', 'user').replace(' ', '.').lower()}@smg.com", # Auto-gen email if missing
                "phone_number": row.get('CONTACT NUMBER', ''),
                "department": row.get('DEPARTMENT', 'General'),
                "designation": row.get('QUALIFICATION', 'Intern'),
                "monthly_stipend": 15000.00 # Default or parse from CSV
            }

            serializer = InternOnboardingSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                success_count += 1
            else:
                errors.append(f"Row {row.get('SNO', '?')}: {serializer.errors}")

        return Response({
            "message": f"Successfully imported {success_count} interns.",
            "errors": errors
        })