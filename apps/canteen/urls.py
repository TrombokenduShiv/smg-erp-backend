from django.urls import path
from .views import PurchaseCouponView, RedeemCouponView

urlpatterns = [
    path('purchase/', PurchaseCouponView.as_view(), name='purchase_coupon'),
    path('redeem/', RedeemCouponView.as_view(), name='redeem_coupon'),
]