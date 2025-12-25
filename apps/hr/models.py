# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class InternProfile(models.Model):
    """
    Stores the "Physical" attributes of the intern shown on Dashboard.
    One-to-One link with the User (Login) model.
    """
    # Link to the Login Account (If User is deleted, Profile is deleted)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Dashboard Data Fields
    designation = models.CharField(max_length=100, default="Intern")
    department = models.CharField(max_length=50, default="IT")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact Number")
    personal_email = models.EmailField(blank=True, help_text="Recovery Email")
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True,
        default='profile_pics/default_avatar.png'
    )

    monthly_stipend = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00)
    
    # Logistics
    joining_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.display_id} - {self.user.first_name}"