import uuid
import datetime
from django.db import models, transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from .utils import increment_seq

# =========================================================
# 1. CUSTOM USER MANAGER
# =========================================================
class User(AbstractUser):
    # 1. Internal ID
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 2. External ID - FIX HERE: Add blank=True
    display_id = models.CharField(
        max_length=12, 
        unique=True, 
        editable=False, 
        blank=True,  # <--- THIS ALLOWS VALIDATION TO PASS WHEN EMPTY
        help_text="The Unique Smart ID (e.g., 25INT1211A01)"
    )
class CustomUserManager(BaseUserManager):
    """
    Custom manager to handle user creation without a 'username' argument.
    It relies on 'email' as the unique identifier for creation, 
    while the Model handles the 'display_id' generation.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        
        email = self.normalize_email(email)
        # Create the user instance
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'SUP') # Force Super Admin Role

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# =========================================================
# 2. USER MODEL
# =========================================================
class User(AbstractUser):
    # 1. Internal ID (Database Only - Zero Trust)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # 2. External ID (Login ID - e.g., 25INT1211A01)
    display_id = models.CharField(
        max_length=12, 
        unique=True, 
        editable=False, 
        help_text="The Unique Smart ID (e.g., 25INT1211A01)"
    )
    is_first_login = models.BooleanField(default=True)
    
    # 3. Roles
    class Role(models.TextChoices):
        INTERN = 'INT', 'Intern'
        DEPT_ADMIN = 'ADM', 'Dept Admin'
        SUPER_ADMIN = 'SUP', 'Super Admin'

    role = models.CharField(max_length=3, choices=Role.choices, default=Role.INTERN)

    # Scope: IT Admin has department='IT'
    department = models.CharField(
        max_length=50, 
        default="General", 
        help_text="The Department this user belongs to (e.g. IT, HR, Sales)"
    )
    
    # REMOVE default username, use display_id for AUTHENTICATION
    username = None 
    USERNAME_FIELD = 'display_id'
    
    # Required for 'createsuperuser' command prompt
    REQUIRED_FIELDS = ['email'] 

    # Link the Custom Manager
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        # Auto-generate Smart ID if it doesn't exist
        if not self.display_id:
            self.display_id = self.generate_smart_id()
        super().save(*args, **kwargs)

    def generate_smart_id(self):
        """
        Logic: YY (Year) + RRR (Role) + MMDD (Date) + SEQ (Sequence)
        """
        today = datetime.date.today()
        yy = today.strftime("%y")   # e.g., "25"
        mmdd = today.strftime("%m%d") # e.g., "1211"
        role_code = self.role       # e.g., "INT"
        
        prefix = f"{yy}{role_code}{mmdd}"
        
        # Atomic Transaction to prevent race conditions
        with transaction.atomic():
            # Find the last user created TODAY with this ROLE
            last_user = User.objects.filter(
                display_id__startswith=prefix
            ).order_by('display_id').last()
            
            if last_user:
                # Extract the last 3 chars (The Sequence)
                try:
                    last_seq = last_user.display_id[-3:]
                    new_seq = increment_seq(last_seq)
                except Exception:
                    new_seq = "001"
            else:
                new_seq = "001"
                
        return f"{prefix}{new_seq}"

    def __str__(self):
        return f"{self.display_id} ({self.role})"