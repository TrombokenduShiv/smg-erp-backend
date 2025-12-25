import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.operations.models import AttendanceLog

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds random attendance data for testing'

    def handle(self, *args, **kwargs):
        # 1. Get the Super Admin (our test user)
        user = User.objects.filter(role='SUP').first()
        if not user:
            self.stdout.write(self.style.ERROR("No Admin found. Run init_genesis first."))
            return

        # 2. Define the Date Range (Current Month)
        today = datetime.date.today()
        start_date = today.replace(day=1)
        
        self.stdout.write(f"Seeding data for {user.display_id} from {start_date} to {today}...")

        # 3. Loop through days
        current_day = start_date
        while current_day <= today:
            # Skip Weekends (Optional logic)
            if current_day.weekday() < 5: # Mon-Fri
                # Randomly choose status: Present (80%), Absent (10%), Late (10%)
                status = random.choices(['P', 'A', 'HD'], weights=[80, 10, 10])[0]
                
                # Update or Create (Idempotent)
                AttendanceLog.objects.update_or_create(
                    user=user,
                    date=current_day,
                    defaults={
                        'check_in': datetime.time(9, 0),
                        'check_out': datetime.time(18, 0),
                        'status': status,
                        'is_finalized': True
                    }
                )
            
            current_day += datetime.timedelta(days=1)

        self.stdout.write(self.style.SUCCESS("Attendance Data Generated Successfully!"))