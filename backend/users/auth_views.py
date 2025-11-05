from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    Custom login view for API authentication
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Get or create token for the user (no session login needed)
                from rest_framework.authtoken.models import Token
                token, created = Token.objects.get_or_create(user=user)
                
                # Get user profile information
                profile_data = None
                try:
                    if hasattr(user, 'profile'):
                        profile_data = {
                            'id': user.profile.id,
                            'role': user.profile.role,
                            'phone': user.profile.phone,
                            'address': user.profile.address,
                            'date_of_birth': user.profile.date_of_birth,
                        }
                except:
                    profile_data = None

                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'profile': profile_data,
                    },
                    'token': token.key
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': 'Account is disabled'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {'error': 'Invalid username or password'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    except json.JSONDecodeError:
        return Response(
            {'error': 'Invalid JSON data'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    """
    Custom logout view - token-based (no session logout needed)
    """
    return Response({'success': True, 'message': 'Logout successful'})
