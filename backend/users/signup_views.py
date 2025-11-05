from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile, StudentProfile
from .serializers import UserSerializer, UserProfileSerializer, StudentProfileSerializer
import random
import string


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """Handle user registration"""
    try:
        with transaction.atomic():
            username = request.data.get('username')
            password = request.data.get('password')
            role = request.data.get('role', 'student')
            
            if not all([username, password]):
                return Response({
                    'success': False,
                    'error': 'Username and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            reserved_usernames = ['admin', 'guest']
            if username.lower() in reserved_usernames:
                return Response({
                    'success': False,
                    'error': 'This username is reserved and cannot be used'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(username=username).exists():
                return Response({
                    'success': False,
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create_user(
                username=username,
                password=password,
                first_name='',
                last_name=''
            )
            
            profile = UserProfile.objects.create(
                user=user,
                role=role,
                phone='',
                address='',
                date_of_birth=None
            )
            
            if role == 'student':
                student_id = generate_student_id()
                
                student_profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    graduation_year=None,
                    gpa=None,
                    enrollment_status='active'
                )
            
            user_serializer = UserSerializer(user)
            profile_serializer = UserProfileSerializer(profile)
            
            response_data = {
                'success': True,
                'message': 'User created successfully',
                'user': user_serializer.data,
                'profile': profile_serializer.data
            }
            
            if role == 'student':
                student_serializer = StudentProfileSerializer(student_profile)
                response_data['student_profile'] = student_serializer.data
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_student_id():
    """Generate a unique student ID"""
    while True:
        # Generate a 8-digit student ID
        student_id = ''.join(random.choices(string.digits, k=8))
        if not StudentProfile.objects.filter(student_id=student_id).exists():
            return student_id


@csrf_exempt
@api_view(['GET'])
def get_user_profile(request):
    """Get current user's profile"""
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
        
        student_profile = None
        if profile.is_student:
            try:
                student_profile = user.student_profile
            except StudentProfile.DoesNotExist:
                pass
        
        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(profile)
        
        response_data = {
            'success': True,
            'user': user_serializer.data,
            'profile': profile_serializer.data
        }
        
        if student_profile:
            student_serializer = StudentProfileSerializer(student_profile)
            response_data['student_profile'] = student_serializer.data
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT'])
def update_user_profile(request):
    """Update current user's profile"""
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({
                'success': False,
                'error': 'User not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.username in ['admin', 'guest']:
            if 'username' in request.data and request.data['username'] != user.username:
                return Response({
                    'success': False,
                    'error': 'Username cannot be changed for admin/guest accounts'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if 'password' in request.data and request.data['password']:
                return Response({
                    'success': False,
                    'error': 'Password cannot be changed for admin/guest accounts'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()
            
            try:
                profile = user.profile
            except UserProfile.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'User profile not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if 'phone' in request.data:
                profile.phone = request.data['phone']
            if 'address' in request.data:
                profile.address = request.data['address']
            if 'date_of_birth' in request.data:
                profile.date_of_birth = request.data['date_of_birth']
            profile.save()
            
            # Update student profile if user is a student
            if profile.is_student:
                try:
                    student_profile = user.student_profile
                    if 'graduation_year' in request.data:
                        student_profile.graduation_year = request.data['graduation_year']
                    if 'gpa' in request.data:
                        student_profile.gpa = request.data['gpa']
                    if 'enrollment_status' in request.data:
                        student_profile.enrollment_status = request.data['enrollment_status']
                    student_profile.save()
                except StudentProfile.DoesNotExist:
                    pass
            
            user_serializer = UserSerializer(user)
            profile_serializer = UserProfileSerializer(profile)
            
            response_data = {
                'success': True,
                'message': 'Profile updated successfully',
                'user': user_serializer.data,
                'profile': profile_serializer.data
            }
            
            if profile.is_student and hasattr(user, 'student_profile'):
                student_serializer = StudentProfileSerializer(user.student_profile)
                response_data['student_profile'] = student_serializer.data
            
            return Response(response_data, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
