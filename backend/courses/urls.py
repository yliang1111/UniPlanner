from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, CourseViewSet, PrerequisiteViewSet,
    DegreeProgramViewSet, DegreeRequirementViewSet,
    CourseRequirementViewSet, CourseOfferingViewSet
)
from .admin_views import (
    admin_courses_list, admin_create_course, admin_update_course, admin_delete_course,
    admin_departments_list, admin_degree_programs_list
)
from .test_admin import test_admin_auth
from .debug_auth import debug_auth
from .simple_admin import simple_admin_courses, simple_admin_departments, simple_admin_degree_programs, simple_admin_create_course, simple_admin_delete_course, simple_admin_update_course
from .program_admin_views import (
    simple_admin_program_types, simple_admin_programs, simple_admin_create_program,
    simple_admin_update_program, simple_admin_delete_program,
    simple_admin_create_program_requirement, simple_admin_create_program_course_requirement
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'prerequisites', PrerequisiteViewSet)
router.register(r'degree-programs', DegreeProgramViewSet)
router.register(r'degree-requirements', DegreeRequirementViewSet)
router.register(r'course-requirements', CourseRequirementViewSet)
router.register(r'offerings', CourseOfferingViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Admin endpoints
    path('admin/courses/', admin_courses_list, name='admin_courses_list'),
    path('admin/courses/create/', admin_create_course, name='admin_create_course'),
    path('admin/courses/<int:course_id>/', admin_update_course, name='admin_update_course'),
    path('admin/courses/<int:course_id>/delete/', admin_delete_course, name='admin_delete_course'),
    path('admin/departments/', admin_departments_list, name='admin_departments_list'),
    path('admin/degree-programs/', admin_degree_programs_list, name='admin_degree_programs_list'),
    # Test endpoint
    path('admin/test/', test_admin_auth, name='test_admin_auth'),
    # Debug endpoint
    path('debug/auth/', debug_auth, name='debug_auth'),
    # Simple admin endpoints (no auth for testing)
    path('simple-admin/courses/', simple_admin_courses, name='simple_admin_courses'),
    path('simple-admin/courses/create/', simple_admin_create_course, name='simple_admin_create_course'),
    path('simple-admin/courses/<int:course_id>/', simple_admin_update_course, name='simple_admin_update_course'),
    path('simple-admin/courses/<int:course_id>/delete/', simple_admin_delete_course, name='simple_admin_delete_course'),
    path('simple-admin/departments/', simple_admin_departments, name='simple_admin_departments'),
    path('simple-admin/degree-programs/', simple_admin_degree_programs, name='simple_admin_degree_programs'),
    
    # Program management endpoints
    path('simple-admin/program-types/', simple_admin_program_types, name='simple_admin_program_types'),
    path('simple-admin/programs/', simple_admin_programs, name='simple_admin_programs'),
    path('simple-admin/programs/create/', simple_admin_create_program, name='simple_admin_create_program'),
    path('simple-admin/programs/<int:program_id>/', simple_admin_update_program, name='simple_admin_update_program'),
    path('simple-admin/programs/<int:program_id>/delete/', simple_admin_delete_program, name='simple_admin_delete_program'),
    path('simple-admin/program-requirements/create/', simple_admin_create_program_requirement, name='simple_admin_create_program_requirement'),
    path('simple-admin/program-course-requirements/create/', simple_admin_create_program_course_requirement, name='simple_admin_create_program_course_requirement'),
]
