from rest_framework import serializers
from .models import LeaveRequest

class LeaveActionSerializer(serializers.Serializer):
    """
    Validates the Admin's decision.
    """
    request_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['APPROVE', 'REJECT'])
    rejection_reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        # Check if the request actually exists
        try:
            leave_request = LeaveRequest.objects.get(id=data['request_id'])
        except LeaveRequest.DoesNotExist:
            raise serializers.ValidationError("Leave Request ID not found.")
        
        # Logic: Can only act on PENDING requests
        if leave_request.current_status != 'PH': # PH = Pending HOD
            raise serializers.ValidationError("This request has already been processed.")
            
        return data