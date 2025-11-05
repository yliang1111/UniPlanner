from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScheduleViewSet, ScheduleItemViewSet, DegreeAuditViewSet, UserCourseSelectionViewSet

router = DefaultRouter()
router.register(r'schedules', ScheduleViewSet)
router.register(r'schedule-items', ScheduleItemViewSet)
router.register(r'degree-audits', DegreeAuditViewSet)
router.register(r'course-selections', UserCourseSelectionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

