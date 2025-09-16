from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleViewSet, ScheduleItemViewSet, DegreeAuditViewSet

router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet)
router.register(r'schedule-items', ScheduleItemViewSet)
router.register(r'degree-audits', DegreeAuditViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

