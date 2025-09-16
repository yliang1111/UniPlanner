from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, StudentProfileViewSet
from .auth_views import login_view, logout_view
from .signup_views import signup_view, get_user_profile, update_user_profile

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', StudentProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', login_view, name='api_login'),
    path('auth/logout/', logout_view, name='api_logout'),
    path('auth/signup/', signup_view, name='api_signup'),
    path('auth/profile/', get_user_profile, name='api_profile'),
    path('auth/profile/update/', update_user_profile, name='api_profile_update'),
]
