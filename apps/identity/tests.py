from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTests(APITestCase):
    def setUp(self):
        # Create a test user for login checks
        self.user_data = {
            'email': 'test@smg.com',
            'password': 'StrongPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'INT',
            'department': 'IT'
        }
        # Note: CustomUserManager creates user with just email/password
        self.user = User.objects.create_user(**self.user_data)

    def test_login_success(self):
        """
        Ensure valid credentials return a JWT Token.
        """
        # Try to find the URL, if 'login' fails, try hardcoded path to debug
        try:
            url = reverse('login')
        except:
            url = '/api/v1/auth/login/'

        data = {
            'email': 'test@smg.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data) # Check for JWT Access Token
        self.assertIn('refresh', response.data)

    def test_login_failure(self):
        """
        Ensure invalid passwords fail.
        """
        try:
            url = reverse('login')
        except:
            url = '/api/v1/auth/login/'

        data = {
            'email': 'test@smg.com',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)