from rest_framework import serializers
from .models import Programme, Application
from apps.identity.serializers import UserSerializer

class ProgrammeSerializer(serializers.ModelSerializer):
    is_eligible = serializers.SerializerMethodField()

    class Meta:
        model = Programme
        fields = [
            'id', 'title', 'description', 'deadline', 
            'form_schema', 'target_department', 'is_eligible', 'created_at'
        ]

    def get_is_eligible(self, obj):
        # Graceful handling if request context is missing
        if 'request' not in self.context:
            return False
        user = self.context['request'].user
        
        # 1. Dept Check
        if obj.target_department and obj.target_department != user.department:
            return False
        # 2. Already Applied Check
        if Application.objects.filter(programme=obj, applicant=user).exists():
            return False
        return True

class ApplicationSerializer(serializers.ModelSerializer):
    applicant_details = UserSerializer(source='applicant', read_only=True)
    
    class Meta:
        model = Application
        fields = ['id', 'programme', 'applicant_details', 'form_data', 'status', 'applied_on']
        read_only_fields = ['applicant', 'status', 'applied_on']

    def validate(self, data):
        """
        DYNAMIC FORM VALIDATION
        Ensures 'form_data' matches the 'programme.form_schema'.
        """
        programme = data['programme']
        user_answers = data.get('form_data', {})
        schema = programme.form_schema # List of dicts: [{'label': 'CV', 'required': True}, ...]

        # 1. Check for Required Fields
        for field in schema:
            label = field.get('label')
            is_required = field.get('required', False)
            
            # If required, key must exist and not be empty
            if is_required and (label not in user_answers or not user_answers[label]):
                raise serializers.ValidationError({
                    "form_data": f"The field '{label}' is required."
                })

        return data