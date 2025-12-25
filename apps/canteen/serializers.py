from rest_framework import serializers
from .models import Coupon

class RedeemCouponSerializer(serializers.Serializer):
    """
    Validates the QR Code scan data.
    """
    coupon_id = serializers.UUIDField(format='hex_verbose')

    def validate_coupon_id(self, value):
        try:
            coupon = Coupon.objects.get(id=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid Coupon ID. Fake or non-existent.")

        if coupon.is_redeemed:
            raise serializers.ValidationError("This coupon has ALREADY been used.")
        
        return value

class CouponSerializer(serializers.ModelSerializer):
    """
    Used to show the User their purchased coupon.
    """
    class Meta:
        model = Coupon
        fields = ['id', 'amount', 'is_redeemed', 'purchased_at', 'redeemed_at']