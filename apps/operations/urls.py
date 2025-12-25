from django.urls import path
from .views import (
    LeaveRequestListCreateView, 
    ManagerInboxView, 
    ApproveLeaveView, 
    MyAttendanceHistoryView, 
    MarkAttendanceView
)

urlpatterns = [
    # --- Intern URLs ---
    # Unified URL: GET to list history, POST to apply
    path('leaves/', LeaveRequestListCreateView.as_view(), name='leave-list-create'),
    
    path('attendance/mark/', MarkAttendanceView.as_view(), name='mark_attendance'), 
    path('my-attendance/', MyAttendanceHistoryView.as_view(), name='my_attendance'),
    
    # --- Admin URLs ---
    path('admin/inbox/', ManagerInboxView.as_view(), name='manager_inbox'),
    
    # The Decision URL now includes the ID (<int:pk>) for safety and clarity
    path('leaves/<int:pk>/decide/', ApproveLeaveView.as_view(), name='leave-decide'),
]