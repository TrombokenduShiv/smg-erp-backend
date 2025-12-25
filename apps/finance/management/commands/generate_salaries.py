import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.finance.services import calculate_stipend
from apps.finance.models import SalarySlip
from apps.finance.tasks import generate_pdf_task

User = get_user_model()

class Command(BaseCommand):
    help = 'Generates Salary Slips for all Interns for a specific month (Format: YYYY-MM)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month', 
            type=str, 
            help='Target month in YYYY-MM format (e.g., 2025-12). Defaults to previous month.'
        )

    def handle(self, *args, **options):
        # 1. Determine the Month
        if options['month']:
            try:
                target_date = datetime.datetime.strptime(options['month'], '%Y-%m').date()
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid format. Use YYYY-MM"))
                return
        else:
            # Default: Last month (If today is Jan, generate for Dec)
            today = timezone.now().date()
            first = today.replace(day=1)
            target_date = first - datetime.timedelta(days=1)
            target_date = target_date.replace(day=1) # Ensure 1st of month

        self.stdout.write(f"Starting Payroll for: {target_date.strftime('%B %Y')}")

        # 2. Fetch Eligible Users (Interns Only)
        interns = User.objects.filter(role='INT', is_active=True)
        count = 0
        
        for intern in interns:
            try:
                # 1. Calculation (Sync)
                slip = calculate_stipend(intern, target_date)
                
                if slip:
                    # 2. PDF Generation (Async / Background)
                    # We pass the ID, not the object, because JSON serialization is faster
                    generate_pdf_task.delay(slip.id)
                    
                    self.stdout.write(self.style.SUCCESS(f"{intern.display_id}: ₹{slip.final_amount} (PDF Queued)"))
                    count += 1
                else:
                    self.stdout.write(self.style.WARNING(f"{intern.display_id}: Skipped"))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"{intern.display_id}: Error - {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n Payroll Complete. Generated {count} slips."))