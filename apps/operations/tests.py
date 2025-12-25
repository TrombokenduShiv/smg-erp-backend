from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.operations.models import LeaveRequest
from datetime import date, timedelta

User = get_user_model()

class LeaveWorkflowTests(APITestCase):
    def setUp(self):
        self.intern = User.objects.create_user(
            email='intern@smg.com', password='pass', role='INT', department='IT'
        )
        self.admin = User.objects.create_user(
            email='admin@smg.com', password='pass', role='ADM', department='IT'
        )
        # Use 'SL' (2 chars)
        self.leave = LeaveRequest.objects.create(
            user=self.intern,
            leave_type='SL', 
            from_date=date.today(),
            to_date=date.today(),
            reason="Sick"
        )
        
        self.apply_url = reverse('leave-list-create')
        self.approve_url = reverse('leave-decide', args=[self.leave.id])

    def test_intern_apply_leave(self):
        self.client.force_authenticate(user=self.intern)
        
        # Use Tomorrow/DayAfter to avoid "Past Date" validation errors
        start = date.today() + timedelta(days=1)
        end = date.today() + timedelta(days=2)

        data = {
            'leave_type': 'CL',  # 2 chars
            'from_date': start,
            'to_date': end,
            'reason': 'Vacation'
        }
        response = self.client.post(self.apply_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_intern_cannot_approve_leave(self):
        self.client.force_authenticate(user=self.intern)
        data = {'action': 'APPROVE'}
        response = self.client.post(self.approve_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

    def test_admin_can_approve_leave(self):
        self.client.force_authenticate(user=self.admin)
        data = {'action': 'APPROVE'}
        response = self.client.post(self.approve_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.leave.refresh_from_db()
        self.assertEqual(self.leave.current_status, 'AP')