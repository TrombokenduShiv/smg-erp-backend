from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'department']
    def create(self, validated_data):
        validated_data['role'] = 'INT'
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['display_id', 'email', 'role', 'department', 'first_name', 'last_name']
        read_only_fields = ['display_id', 'role']

class AdminCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'department', 'role']
    def create(self, validated_data):
        password = "ChangeMe@123" 
        user = User.objects.create_user(
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            department=validated_data['department']
        )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    def validate_new_password(self, value):
        validate_password(value)
        return value

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # FIX: Override __init__ to remove the default 'required' constraint on display_id
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Make display_id optional (so input validation passes without it)
        self.fields[User.USERNAME_FIELD] = serializers.CharField(required=False, read_only=True)
        # 2. Make email required
        self.fields['email'] = serializers.EmailField(required=True)

    def validate(self, attrs):
        # 3. Map Email -> Display ID
        email = attrs.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                attrs[User.USERNAME_FIELD] = user.display_id 
            except User.DoesNotExist:
                # If user doesn't exist, we do nothing. 
                # super().validate() will fail auth naturally (401).
                pass
        
        # 4. Authenticate
        data = super().validate(attrs)
        
        # 5. Add Custom Claims
        data['role'] = self.user.role
        data['is_first_login'] = self.user.is_first_login
        data['display_id'] = self.user.display_id
        data['full_name'] = f"{self.user.first_name} {self.user.last_name}"
        data['department'] = getattr(self.user, 'department', 'N/A')
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        return value

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    token = serializers.CharField()
    uidb64 = serializers.CharField()
    def validate(self, attrs):
        try:
            uid = urlsafe_base64_decode(attrs['uidb64']).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError("Invalid link")
        if not PasswordResetTokenGenerator().check_token(user, attrs['token']):
            raise serializers.ValidationError("Invalid token")
        attrs['user'] = user
        return attrs