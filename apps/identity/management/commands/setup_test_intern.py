from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import datetime
import random

# -----------------------------------------------------------------------------
# ⚠️ ACTION REQUIRED: Verify these import paths match your project structure
# -----------------------------------------------------------------------------
# Assuming InternProfile is in apps.profiles or apps.identity
from apps.hr.models import InternProfile
# Assuming AttendanceLog and LeaveRequest are in apps.attendance or similar
from apps.operations.models import AttendanceLog, LeaveRequest 
# Assuming SalarySlip is in apps.payroll
from apps.finance.models import SalarySlip 
# -----------------------------------------------------------------------------

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a fully onboarded test Intern account with related profile, attendance, and payroll data.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting Full Intern Onboarding Simulation...'))

        test_email = "intern.test@smg.com"
        test_pass = "TestPassword123!"

        try:
            with transaction.atomic():
                # 1. CLEANUP: Remove existing test user
                if User.objects.filter(email=test_email).exists():
                    self.stdout.write(self.style.ERROR(f'   User {test_email} exists. Deleting...'))
                    User.objects.get(email=test_email).delete()

                # 2. USER ACCOUNT: Create the Login
                # We instantiate and save() manually to trigger your smart ID generation logic
                user = User(
                    email=test_email,
                    first_name="Test",
                    last_name="Intern",
                    role=User.Role.INTERN,
                    is_active=True,
                    is_first_login=True
                )
                user.set_password(test_pass)
                user.save() 
                self.stdout.write(self.style.SUCCESS(f'   ✓ User Created: {user.display_id}'))

                # 3. PROFILE: Create the Physical Profile
                InternProfile.objects.create(
                    user=user,
                    designation="SDE Intern",
                    department="Engineering",
                    phone_number="9876543210",
                    personal_email="personal.test@gmail.com",
                    monthly_stipend=25000.00
                )
                self.stdout.write(self.style.SUCCESS('   ✓ Intern Profile Linked'))

                # 4. ATTENDANCE: Generate last 7 days of logs
                # Pattern: 5 Days Present, 1 Half Day, 1 Absent
                today = timezone.now().date()
                for i in range(7):
                    log_date = today - datetime.timedelta(days=i)
                    
                    # Skip if specific logic needed (e.g. weekends), but for now we just dump data
                    status = AttendanceLog.Status.PRESENT
                    check_in = datetime.time(9, 30)
                    check_out = datetime.time(18, 30)

                    # Make yesterday Absent for variety
                    if i == 1:
                        status = AttendanceLog.Status.ABSENT
                        check_in = None
                        check_out = None
                    # Make 3 days ago a Half Day
                    elif i == 3:
                        status = AttendanceLog.Status.HALF_DAY
                        check_in = datetime.time(10, 0)
                        check_out = datetime.time(14, 0)

                    AttendanceLog.objects.create(
                        user=user,
                        date=log_date,
                        status=status,
                        check_in=check_in,
                        check_out=check_out,
                        is_finalized=True
                    )
                self.stdout.write(self.style.SUCCESS('   ✓ Last 7 Days Attendance Generated'))

                # 5. LEAVES: Create dummy requests
                # A pending Sick Leave
                LeaveRequest.objects.create(
                    user=user,
                    leave_type=LeaveRequest.LeaveType.MEDICAL,
                    from_date=today + datetime.timedelta(days=5),
                    to_date=today + datetime.timedelta(days=6),
                    reason="Scheduled dental surgery",
                    current_status=LeaveRequest.RequestStatus.PENDING_HOD
                )
                # An approved Casual Leave (from the past)
                LeaveRequest.objects.create(
                    user=user,
                    leave_type=LeaveRequest.LeaveType.CASUAL,
                    from_date=today - datetime.timedelta(days=10),
                    to_date=today - datetime.timedelta(days=10),
                    reason="Family function",
                    current_status=LeaveRequest.RequestStatus.APPROVED
                )
                self.stdout.write(self.style.SUCCESS('   ✓ Leave Requests (Pending & Approved) Added'))

                # 6. PAYROLL: Create last month's salary slip
                last_month = today.replace(day=1) - datetime.timedelta(days=1)
                slip_month = last_month.replace(day=1) # 1st of previous month
                
                SalarySlip.objects.create(
                    user=user,
                    month=slip_month,
                    base_amount=25000.00,
                    present_days=28,
                    total_working_days=30,
                    final_amount=23500.00, # Just a dummy calculation
                    status=SalarySlip.Status.PAID
                )
                self.stdout.write(self.style.SUCCESS('   ✓ Salary Slip Generated'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n Critical Error: {str(e)}'))
            # Transaction atomic will auto-rollback here
            return

        # ---------------------------------------------------------
        # Final Output
        # ---------------------------------------------------------
        self.stdout.write(self.style.SUCCESS('\n=========================================='))
        self.stdout.write(self.style.SUCCESS('      INTERN ONBOARDING COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=========================================='))
        self.stdout.write(f'Name:       Test Intern')
        self.stdout.write(f'Smart ID:   {user.display_id}') 
        self.stdout.write(f'Login:      {test_email}')
        self.stdout.write(f'Password:   {test_pass}')
        self.stdout.write(f'Joined:     {datetime.date.today()}')
        self.stdout.write(self.style.SUCCESS('=========================================='))