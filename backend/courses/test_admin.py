from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_admin_auth(request):
    """Test admin authentication"""
    user = request.user
    try:
        profile = user.profile
        is_admin = profile.role == 'admin' and user.username != 'guest'
        return Response({
            'user': user.username,
            'is_authenticated': user.is_authenticated,
            'has_profile': hasattr(user, 'profile'),
            'profile_role': profile.role if hasattr(user, 'profile') else None,
            'is_admin': is_admin,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'user': user.username,
            'is_authenticated': user.is_authenticated,
        })

