import datetime
from django.db.models import Count, Q
from apps.operations.models import AttendanceLog
from apps.finance.models import SalarySlip

def calculate_stipend(user, month_date):
    """
    The Core Financial Formula.
    month_date: A date object (e.g., 2025-12-01)
    """
    # 1. Fetch Base Stipend
    try:
        base_stipend = user.profile.monthly_stipend
    except:
        return None # No profile, no salary

    # 2. Calculate Dates
    # Simple logic: Start of month to End of month
    # For MVP, we treat every month as 30 days standard
    total_days = 30 
    
    # 3. Count Attendance (From Operations App)
    # We count Present (P) AND Half Days (HD)
    # Note: Policy might say HD = 0.5, but for simplicity let's say HD counts as Present for now
    logs = AttendanceLog.objects.filter(
        user=user,
        date__month=month_date.month,
        date__year=month_date.year
    )
    
    stats = logs.aggregate(
        present=Count('id', filter=Q(status='P')),
        half_day=Count('id', filter=Q(status='HD'))
    )
    
    # Calculate Effective Days (Present + 0.5 * HalfDay)
    present_days = (stats['present'] or 0) + ((stats['half_day'] or 0) * 0.5)
    
    # 4. The Formula
    # (Base / 30) * Present
    daily_rate = float(base_stipend) / total_days
    final_amount = daily_rate * float(present_days)
    
    # 5. Save Record (Idempotent)
    slip, created = SalarySlip.objects.update_or_create(
        user=user,
        month=month_date.replace(day=1),
        defaults={
            'base_amount': base_stipend,
            'present_days': present_days,
            'total_working_days': total_days,
            'final_amount': round(final_amount, 2),
            'status': 'GEN'
        }
    )
    
    return slip