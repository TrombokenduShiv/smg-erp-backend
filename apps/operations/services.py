from django.db.models import Count, Q
from .models import AttendanceLog, LeaveRequest
import datetime

def get_dashboard_stats(user):
    """
    Calculates the numbers for the Dashboard Pie Chart & Progress Bars.
    """
    today = datetime.date.today()
    current_month_start = today.replace(day=1)
    
    # 1. Calculate Attendance (Pie Chart Data)
    logs = AttendanceLog.objects.filter(
        user=user, 
        date__gte=current_month_start
    )
    
    stats = logs.aggregate(
        present=Count('id', filter=Q(status='P')),
        absent=Count('id', filter=Q(status='A')),
        late=Count('id', filter=Q(status='HD'))
    )
    
    # 2. Calculate Leaves (Progress Bar Data)
    # Logic: Count approved leaves in current year
    approved_leaves = LeaveRequest.objects.filter(
        user=user,
        current_status='AP',
        from_date__year=today.year
    ).count()

    return {
        "attendance": {
            "present": stats['present'] or 0,
            "absent": stats['absent'] or 0,
            "half_day": stats['late'] or 0,
            "total_working_days": 22, # Hardcoded for now, dynamic later
        },
        "leaves": {
            "used": approved_leaves,
            "total_allowed": 12 # Standard Policy
        }
    }