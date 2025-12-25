from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from .models import Coupon
from .serializers import RedeemCouponSerializer, CouponSerializer
from .permissions import IsCanteenStaff # Import our custom permission

class PurchaseCouponView(APIView):
    """
    POST /api/v1/canteen/purchase/
    Intern buys a coupon.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # TODO: Link this to Finance App to deduct balance from 'Wallet'
        # For now, we assume infinite credit (MVP)
        
        coupon = Coupon.objects.create(user=request.user, amount=50.00)
        
        serializer = CouponSerializer(coupon)
        return Response({
            "message": "Coupon Purchased Successfully",
            "data": serializer.data,
            "qr_code_string": f"{coupon.id}" # The frontend converts this string to a QR image
        }, status=status.HTTP_201_CREATED)

class RedeemCouponView(APIView):
    """
    POST /api/v1/canteen/redeem/
    Canteen Staff scans the QR code.
    """
    # 1. Apply the Security Guard
    permission_classes = [IsCanteenStaff] 

    def post(self, request):
        # 2. Validate the Input (UUID format, Existence, Used status)
        serializer = RedeemCouponSerializer(data=request.data)
        
        if serializer.is_valid():
            coupon_id = serializer.validated_data['coupon_id']
            
            # 3. Perform Logic (Atomic Update)
            coupon = Coupon.objects.get(id=coupon_id)
            coupon.is_redeemed = True
            coupon.redeemed_at = timezone.now()
            coupon.save()

            return Response({
                "message": "✅ Coupon Valid. Serve Meal.",
                "intern": coupon.user.get_full_name()
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)