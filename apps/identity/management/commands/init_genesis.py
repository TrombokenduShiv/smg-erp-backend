import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates the FIRST Super Admin (Genesis Node)'

    def handle(self, *args, **kwargs):
        # 1. Check if Admin already exists
        if User.objects.filter(role='SUP').exists():
            self.stdout.write(self.style.WARNING('Genesis Admin already exists.'))
            return

        # 2. Generate Secure Random Password
        temp_pass = secrets.token_urlsafe(10)
        
        # 3. Create the User MANUALLY (Bypassing create_superuser to avoid username error)
        try:
            admin = User(
                email="root@smg.com",
                role='SUP',
                is_first_login=True,
                is_staff=True,       # Essential for Admin Panel access
                is_superuser=True,   # Essential for Permissions
                first_name="Genesis",
                last_name="Admin"
            )
            admin.set_password(temp_pass) # Hashes the password securely
            admin.save() # <--- This triggers the 'generate_smart_id' logic in your models.py!

            self.stdout.write(self.style.SUCCESS(f'GENESIS COMPLETE.'))
            self.stdout.write(f'--------------------------------------------------')
            self.stdout.write(f'User ID : {admin.display_id}')
            self.stdout.write(f'Password: {temp_pass}')
            self.stdout.write(f'--------------------------------------------------')
            self.stdout.write('IMPORTANT: Copy these credentials immediately.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating admin: {str(e)}'))