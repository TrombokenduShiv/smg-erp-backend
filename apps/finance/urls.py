from django.urls import path
from .views import MySalaryHistoryView

urlpatterns = [
    path('slips/', MySalaryHistoryView.as_view(), name='my-salary-slips'),
]