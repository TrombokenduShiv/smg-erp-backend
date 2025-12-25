import csv
import io
import boto3
from django.conf import settings
from django.db.models import Q  # <--- FIXED IMPORT
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Programme, Application
from .serializers import ProgrammeSerializer, ApplicationSerializer
# Ensure permissions.py exists with these classes, or use standard IsAuthenticated for now
# from .permissions import IsProgramViewerOrAdmin 

class ProgrammeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProgrammeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['SUP', 'ADM']:
            return Programme.objects.all().order_by('-created_at')
        
        # Intern Logic
        qs = Programme.objects.filter(is_active=True, deadline__gte=timezone.now())
        if user.department:
             qs = qs.filter(Q(target_department="") | Q(target_department=user.department))
        return qs.order_by('deadline')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApplicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user = self.request.user
        # 1. Super Admin
        if user.role == 'SUP':
            return Application.objects.all()
        
        # 2. Viewer/Creator (Admins)
        # Check if user is creator OR in assigned_viewers
        return Application.objects.filter(
            Q(programme__created_by=user) | Q(programme__assigned_viewers=user) | Q(applicant=user)
        ).distinct()

    def perform_create(self, serializer):
        programme = serializer.validated_data['programme']
        user = self.request.user
        
        # Double Check Eligibility (Backend Enforcement)
        if programme.target_department and programme.target_department != user.department:
            raise serializers.ValidationError("Not eligible for this department.")
            
        if Application.objects.filter(programme=programme, applicant=user).exists():
             raise serializers.ValidationError("Already applied.")

        serializer.save(applicant=user)

    # SECURE EXPORT
    @action(detail=False, methods=['get'], url_path='export-csv/(?P<program_id>[^/.]+)')
    def export_csv(self, request, program_id=None):
        """
        Download CSV. Secured manually.
        """
        # 1. Manual Security Check
        program = Programme.objects.filter(id=program_id).first()
        if not program:
            return Response({"error": "Not Found"}, status=404)

        user = request.user
        # Only Creator, Super Admin, or Assigned Viewer can export
        is_authorized = (
            user.role == 'SUP' or 
            program.created_by == user or 
            program.assigned_viewers.filter(id=user.id).exists()
        )
        
        if not is_authorized:
             return Response({"error": "Unauthorized to export data"}, status=403)

        # 2. Generate CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="responses_{program_id}.csv"'

        apps = Application.objects.filter(programme_id=program_id)
        
        # Headers
        headers = ['Applicant Name', 'Email', 'Applied On', 'Status']
        dynamic_keys = [field['label'] for field in program.form_schema] 
        headers.extend(dynamic_keys)

        writer = csv.writer(response)
        writer.writerow(headers)

        for app in apps:
            row = [
                app.applicant.get_full_name(),
                app.applicant.email,
                app.applied_on.strftime("%Y-%m-%d"),
                app.status
            ]
            for field in program.form_schema:
                # Safe .get() in case schema changed after submission
                row.append(app.form_data.get(field['label'], ""))
            writer.writerow(row)

        return response
    
    @action(detail=True, methods=['post'])
    def trigger_export(self, request, pk=None):
        """
        Saves CSV to S3 (Private Bucket).
        """
        if request.user.role != 'SUP':
            return Response({"error": "Only Super Admins can trigger Cloud Sync"}, status=403)

        program = self.get_object()
        apps = Application.objects.filter(programme=program)
        
        # CSV in Memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        headers = ['Applicant', 'Email', 'Status', 'Applied On'] + [f['label'] for f in program.form_schema]
        writer.writerow(headers)
        
        for app in apps:
            row = [app.applicant.get_full_name(), app.applicant.email, app.status, str(app.applied_on)]
            for field in program.form_schema:
                row.append(app.form_data.get(field['label'], ''))
            writer.writerow(row)
            
        # Upload to S3
        try:
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Use a specific folder in the MAIN bucket to keep it simple, or a specific bucket if configured
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME 
            file_key = f"secure_exports/program_{program.id}_{program.title}.csv"
            
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=output.getvalue(),
                ContentType='text/csv',
                ACL='private' # Explicitly Private
            )
            return Response({"message": f"Synced to s3://{bucket_name}/{file_key}"})
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)