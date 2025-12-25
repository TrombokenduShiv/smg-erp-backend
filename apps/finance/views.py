from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import SalarySlip
from .serializers import SalarySlipSerializer
from apps.identity.permissions import IsOwnerOrAdmin

class MySalaryHistoryView(generics.ListAPIView):
    """
    GET /api/v1/finance/slips/
    Returns all salary slips generated for the logged-in user.
    """
    serializer_class = SalarySlipSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        # Return slips ordered by latest month first
        return SalarySlip.objects.filter(user=self.request.user).order_by('-month')