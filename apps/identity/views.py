from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status, permissions, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# Import all necessary serializers
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetRequestSerializer,
    SetNewPasswordSerializer,
    AdminCreationSerializer,
    ChangePasswordSerializer,
    LogoutSerializer
)
# Import permissions (Ensure IsSuperAdmin is defined in permissions.py)
from .permissions import IsSuperAdmin
from apps.common.tasks import send_email_task

User = get_user_model()

# =========================================================
# 1. AUTHENTICATION & SESSION
# =========================================================

class RegisterInternView(APIView):
    """
    POST /api/v1/identity/register/
    Public endpoint for Interns to sign up.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful. Please login.",
                "user_id": user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLoginView(TokenObtainPairView):
    """
    POST /api/v1/identity/login/
    Returns JWT Access & Refresh Tokens + User Role Data.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    """
    POST /api/v1/identity/logout/
    Blacklists the Refresh Token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try:
                token = RefreshToken(serializer.validated_data['refresh'])
                token.blacklist()
                return Response({"message": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
            except Exception:
                return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================================================
# 2. USER PROFILE & MANAGEMENT
# =========================================================

class UserProfileView(APIView):
    """
    GET /api/v1/identity/my-profile/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """
    POST /api/v1/identity/change-password/
    Forces a password change (Good for 'Is First Login' flow).
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.is_first_login = False # Update flag
            user.save()
            return Response({"message": "Password updated successfully."})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateDeptAdminView(APIView):
    """
    POST /api/v1/identity/admin/create/
    Only Super Admins can create Dept Admins.
    """
    permission_classes = [IsSuperAdmin] # Strict RBAC

    def post(self, request):
        serializer = AdminCreationSerializer(data=request.data)
        if serializer.is_valid():
            admin = serializer.save()
            return Response({
                "message": f"Admin {admin.email} created for {admin.department}",
                "default_password": "ChangeMe@123"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =========================================================
# 3. PASSWORD RESET WORKFLOW (Public)
# =========================================================

class RequestPasswordResetView(APIView):
    """
    POST /api/v1/identity/password-reset/request/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.filter(email=email).first()
            
            if user:
                token = PasswordResetTokenGenerator().make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = f"http://localhost:3000/reset-password/{uid}/{token}/"
                
                subject = "Reset Your Password - SMG Portal"
                message = f"Hi {user.first_name},\n\nClick link: {reset_link}"
                send_email_task.delay(subject, message, [user.email])
            
            return Response({"message": "If an account exists, a reset link has been sent."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordView(APIView):
    """
    POST /api/v1/identity/password-reset/confirm/
    """
    permission_classes = [permissions.AllowAny]

    def patch(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)