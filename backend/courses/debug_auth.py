from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_auth(request):
    """Debug authentication status"""
    return Response({
        'user': request.user.username if request.user.is_authenticated else 'Anonymous',
        'is_authenticated': request.user.is_authenticated,
        'session_key': request.session.session_key,
        'session_data': dict(request.session),
        'cookies': dict(request.COOKIES),
        'headers': dict(request.headers),
    })

