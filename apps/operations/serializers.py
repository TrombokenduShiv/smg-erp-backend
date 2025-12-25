from rest_framework import serializers
from .models import LeaveRequest, AttendanceLog
from django.utils import timezone

class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'from_date', 'to_date', 'reason']

    def validate(self, data):
        if data['from_date'] > data['to_date']:
            raise serializers.ValidationError("End date cannot be before start date.")
        if data['from_date'] < timezone.now().date():
            raise serializers.ValidationError("Cannot apply for past dates.")
        return data

class LeaveActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['APPROVE', 'REJECT'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data['action'] == 'REJECT' and not data.get('rejection_reason'):
            raise serializers.ValidationError({"rejection_reason": "Reason is required when rejecting."})
        return data

class LeaveRequestSerializer(serializers.ModelSerializer):
    """
    Used for Lists (History & Inbox)
    """
    status_display = serializers.CharField(source='get_current_status_display', read_only=True)
    applicant_name = serializers.CharField(source='user.get_full_name', read_only=True) # Helpful for Admin
    department = serializers.CharField(source='user.department', read_only=True) # Helpful for Admin

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'applicant_name', 'department', 
            'leave_type', 'from_date', 'to_date', 
            'reason', 'current_status', 'status_display', 
            'applied_on', 'rejection_reason'
        ]
        read_only_fields = ['current_status', 'applied_on', 'rejection_reason']

class AttendanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceLog
        fields = ['date', 'check_in', 'check_out', 'status', 'is_finalized']