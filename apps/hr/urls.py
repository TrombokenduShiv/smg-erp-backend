from django.urls import path
from .views import DashboardView, OnboardInternView, BulkImportInternsView

urlpatterns = [
    # The endpoint that powers the Main Dashboard
    path('dashboard/', DashboardView.as_view(), name='intern_dashboard'),

    # Onboard New Intern
    path('onboard-intern/', OnboardInternView.as_view(), name='onboard_intern'),

    # Bulk Import Interns via CSV
    path('bulk-import/', BulkImportInternsView.as_view(), name='bulk_import'),
]