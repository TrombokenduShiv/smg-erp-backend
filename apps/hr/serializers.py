from rest_framework import serializers
from apps.hr.models import InternProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class DashboardSerializer(serializers.ModelSerializer):
    """
    The 'Master' serializer for the Dashboard.
    It fetches data from both User table and Profile table.
    """
    # Fetch fields from the related User model
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    display_id = serializers.CharField(source='user.display_id')
    email = serializers.EmailField(source='user.email')
    
    class Meta:
        model = InternProfile
        fields = [
            'first_name', 
            'last_name', 
            'display_id', 
            'email',
            'designation', 
            'phone_number', 
            'joining_date',
            'monthly_stipend',
            'profile_picture'
        ]

from django.db import transaction

class InternOnboardingSerializer(serializers.Serializer):
    """
    Takes raw data (Email, Name, Stipend) and creates a full Intern entity.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    department = serializers.CharField()
    designation = serializers.CharField()
    phone_number = serializers.CharField()
    monthly_stipend = serializers.DecimalField(max_digits=10, decimal_places=2)

    def create(self, validated_data):
        # ATOMIC TRANSACTION: Everything succeeds or nothing happens
        with transaction.atomic():
            # 1. Create User (Identity)
            # Password defaults to 'Welcome@123' (User must change it)
            user = User.objects.create_user(
                email=validated_data['email'],
                password="Welcome@123", 
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                role='INT', # Role is strictly Intern
                department=validated_data['department'],
                is_first_login=True
            )
            
            # 2. Create Profile (HR Data)
            InternProfile.objects.create(
                user=user,
                designation=validated_data['designation'],
                department=validated_data['department'],
                phone_number=validated_data['phone_number'],
                monthly_stipend=validated_data['monthly_stipend']
            )
            
            return user