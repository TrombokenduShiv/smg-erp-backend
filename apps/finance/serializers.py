from rest_framework import serializers
from .models import SalarySlip

class SalarySlipSerializer(serializers.ModelSerializer):
    month_str = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = SalarySlip
        fields = [
            'id', 'month', 'month_str', 
            'base_amount', 'present_days', 'total_working_days', 
            'final_amount', 'status', 'status_display', 'generated_on'
        ]

    def get_month_str(self, obj):
        return obj.month.strftime("%B %Y") 