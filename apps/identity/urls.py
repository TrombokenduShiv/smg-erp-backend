from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserProfileView, CreateDeptAdminView, ChangePasswordView, LogoutView, CustomLoginView, RequestPasswordResetView, SetNewPasswordView

urlpatterns = [
    # 1. Login (Get Token) - Built-in JWT view
    path('login/', CustomLoginView.as_view(), name='token_obtain_pair'),
    
    # 2. Refresh Token (Keep session alive)
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 3. Get User Profile
    path('me/', UserProfileView.as_view(), name='user_profile'),
    
    # 4. Create Department Admin (Super Admin Only)
    path('create-admin/', CreateDeptAdminView.as_view(), name='create_admin'),

    # 5. Change Password
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # 6. Logout (Blacklist Refresh Token)
    path('logout/', LogoutView.as_view(), name='auth_logout'),

    # 7. Change Password
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),

    # 8. Request Password Reset
    path('password-reset/request/', RequestPasswordResetView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', SetNewPasswordView.as_view(), name='password_reset_confirm'),
]