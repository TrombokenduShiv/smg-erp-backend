# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AttendanceLog(models.Model):
    """
    Daily Attendance Record.
    Powers the 'Attendance Chart' on the Dashboard.
    """
    class Status(models.TextChoices):
        PRESENT = 'P', 'Present'
        ABSENT = 'A', 'Absent'
        HALF_DAY = 'HD', 'Half Day'
        HOLIDAY = 'H', 'Holiday'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_logs')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.ABSENT)
    
    # Audit Trail (Who modified this? The Time Office Admin?)
    is_finalized = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'date') # One log per user per day

    def __str__(self):
        return f"{self.user.display_id} - {self.date} - {self.status}"


class LeaveRequest(models.Model):
    """
    Leave Application Workflow.
    Powers the 'Used Leaves' progress bar.
    """
    class LeaveType(models.TextChoices):
        CASUAL = 'CL', 'Casual Leave'
        MEDICAL = 'ML', 'Medical Leave'
        
    class RequestStatus(models.TextChoices):
        PENDING_HOD = 'PH', 'Pending HOD'
        PENDING_HR = 'PR', 'Pending HR'
        APPROVED = 'AP', 'Approved'
        REJECTED = 'RJ', 'Rejected'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=2, choices=LeaveType.choices)
    from_date = models.DateField()
    to_date = models.DateField()
    reason = models.TextField()
    
    # The Saga State (Workflow Engine)
    current_status = models.CharField(max_length=2, choices=RequestStatus.choices, default=RequestStatus.PENDING_HOD)
    
    applied_on = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.display_id} : {self.leave_type} ({self.current_status})"