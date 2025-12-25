import io
from celery import shared_task
from django.template.loader import get_template
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from .models import SalarySlip

@shared_task
def generate_pdf_task(slip_id):
    """
    Background Task: 
    1. Fetches the SalarySlip data.
    2. Renders HTML.
    3. Converts to PDF.
    4. Saves it to S3.
    """
    try:
        slip = SalarySlip.objects.get(id=slip_id)
        
        # 1. Prepare Data for Template
        context = {
            'user': slip.user,
            'month_str': slip.month.strftime("%B %Y"),
            'base_amount': slip.base_amount,
            'present_days': slip.present_days,
            'total_working_days': slip.total_working_days,
            'final_amount': slip.final_amount,
            'generated_on': slip.generated_on.strftime("%Y-%m-%d")
        }
        
        # 2. Render HTML
        template = get_template('finance/salary_slip.html')
        html = template.render(context)
        
        # 3. Create PDF (In-Memory)
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
        
        if pisa_status.err:
            return f"Error generating PDF for Slip {slip_id}"
            
        # 4. Save to S3 (Model FileField handles the S3 upload logic automatically)
        file_name = f"Payslip_{slip.user.display_id}_{slip.month.strftime('%m_%Y')}.pdf"
        slip.pdf_file.save(file_name, ContentFile(pdf_buffer.getvalue()))
        slip.save()
        
        return f"PDF Generated: {file_name}"

    except SalarySlip.DoesNotExist:
        return "Slip not found"
    except Exception as e:
        return f"Failed: {str(e)}"