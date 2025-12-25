# Create your models here.
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Programme(models.Model):
    """
    Represents a Scholarship, Hackathon, or Event.
    Stores the 'Form Schema' (Questions) dynamically.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateTimeField()
    
    # DYNAMIC FORM SCHEMA
    # Example: [{"id": "q1", "label": "Upload CV", "type": "file", "required": true}]
    form_schema = models.JSONField(default=list, help_text="The structure of the form questions")
    
    # TARGETING LOGIC
    # If 'target_department' is set, only users from that dept can apply.
    # If blank, it is open to ALL departments.
    target_department = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        help_text="Leave empty for Open to All. Set 'IT' to restrict to IT dept."
    )
    
    # ACCESS CONTROL (Viewers)
    # Who can see the APPLICATIONS? (e.g., The Hiring Manager for this specific event)
    # The Creator and Super Admins have implied access.
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_programs')
    assigned_viewers = models.ManyToManyField(
        User, 
        related_name='viewable_programs', 
        blank=True,
        help_text="Specific users who are allowed to view the responses for this program."
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    """
    A User's response to a Programme.
    """
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        REJECTED = 'REJECTED', 'Rejected'
        ACCEPTED = 'ACCEPTED', 'Accepted'

    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_applications')
    
    # DYNAMIC ANSWERS
    # Example: {"q1": "https://s3.aws/cv.pdf", "q2": "John Doe"}
    form_data = models.JSONField(default=dict)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    applied_on = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('programme', 'applicant') # User can only apply once per program

    def __str__(self):
        return f"{self.applicant.display_id} - {self.programme.title}"