import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Central Handler for all SMG Alerts.
    Uses AWS SES for Emails and AWS SNS for SMS.
    """
    
    def __init__(self):
        # Initialize AWS Clients
        self.ses = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.sns = boto3.client(
            'sns',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def send_email(self, to_email, subject, body_text):
        """
        Sends a transactional email via SES.
        """
        try:
            response = self.ses.send_email(
                Source=settings.DEFAULT_FROM_EMAIL, # Must be verified in Sandbox
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body_text}}
                }
            )
            logger.info(f"Email sent to {to_email}: {response['MessageId']}")
            return True
        except Exception as e:
            logger.error(f"Email Failed: {str(e)}")
            return False

    def send_sms(self, phone_number, message):
        """
        Sends an SMS via SNS.
        phone_number must include country code (e.g., +91...)
        """
        try:
            # SNS Publish
            self.sns.publish(
                PhoneNumber=phone_number,
                Message=f"[SMG Portal] {message}" # Branding prefix
            )
            logger.info(f"SMS sent to {phone_number}")
            return True
        except Exception as e:
            logger.error(f"SMS Failed: {str(e)}")
            return False

    def alert_onboarding(self, user, password):
        """
        Preset: Welcome Email logic
        """
        subject = "Welcome to SMG Group - Account Credentials"
        body = f"""
        Dear {user.first_name},
        
        Welcome to SMG! Your intern portal account has been created.
        
        Smart ID: {user.display_id}
        Temporary Password: {password}
        
        Please login at: {settings.FRONTEND_URL}/login
        
        NOTE: For security, change your password after first login.

        Regards,
        HR Team
        """
        self.send_email(user.email, subject, body)

    def alert_leave_status(self, leave_request):
        """
        Preset: Leave Decision logic
        """
        user = leave_request.user
        status = leave_request.get_current_status_display()
        
        # 1. Send Email
        subject = f"Leave Request Update: {status}"
        body = f"Your leave request for {leave_request.from_date} has been {status}."
        self.send_email(user.email, subject, body)
        
        # 2. Send SMS (Only if number exists)
        # Assuming InternProfile has phone_number
        if hasattr(user, 'profile') and user.profile.phone_number:
            # Ensure +91 prefix for India
            phone = user.profile.phone_number
            if not phone.startswith('+'):
                phone = f"+91{phone}"
            
            self.send_sms(phone, f"Your leave request status is now: {status}.")

from .tasks import send_email_task

class NotificationService:
    def alert_leave_status(self, leave_request):
        subject = f"Leave Update: {leave_request.get_current_status_display()}"
        message = f"Hello {leave_request.user.first_name},\n\nYour leave request for {leave_request.from_date} has been {leave_request.get_current_status_display()}."
        
        recipient = leave_request.user.email
        
        if recipient:
            # .delay() is what hands it off to Celery!
            send_email_task.delay(subject, message, [recipient])