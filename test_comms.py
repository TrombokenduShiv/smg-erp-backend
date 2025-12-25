import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.common.notifications import NotificationService

def test_alerts():
    notifier = NotificationService()

    # 1. Test Email 
    target_email = "trombokendu@gmail.com" 
    print(f"📧 Sending Email to {target_email}...")
    notifier.send_email(target_email, "SMG Test", "This is a test from the Cloud Portal.")

    # 2. Test SMS (Replace with YOUR verified phone)
    target_phone = "+919774306226" 
    print(f"📱 Sending SMS to {target_phone}...")
    notifier.send_sms(target_phone, "System Integration Test Successful!")

if __name__ == "__main__":
    test_alerts()