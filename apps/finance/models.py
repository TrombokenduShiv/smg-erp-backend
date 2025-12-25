from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SalarySlip(models.Model):
    class Status(models.TextChoices):
        GENERATED = 'GEN', 'Generated'
        PAID = 'PAID', 'Paid'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='salary_slips')
    month = models.DateField(help_text="The 1st of the month this slip belongs to")
    
    # Calculation Fields
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    present_days = models.IntegerField()
    total_working_days = models.IntegerField()
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # NEW FIELD: The PDF File
    # upload_to='salary_slips/' ensures it goes to a specific folder in S3
    pdf_file = models.FileField(upload_to='salary_slips/', null=True, blank=True)
    
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.GENERATED)
    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"{self.user.display_id} - {self.month.strftime('%b %Y')}"