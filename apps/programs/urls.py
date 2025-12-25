from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProgrammeViewSet, ApplicationViewSet

router = DefaultRouter()
router.register(r'manage', ProgrammeViewSet, basename='programs')
router.register(r'apply', ApplicationViewSet, basename='applications')

urlpatterns = [
    path('', include(router.urls)),
]