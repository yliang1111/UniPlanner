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
            # Extract data from request
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            first_name = request.data.get('first_name', '')
            last_name = request.data.get('last_name', '')
            role = request.data.get('role', 'student')
            
            # Validate required fields
            if not all([username, email, password]):
                return Response({
                    'success': False,
                    'error': 'Username, email, and password are required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                return Response({
                    'success': False,
                    'error': 'Username already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if User.objects.filter(email=email).exists():
                return Response({
                    'success': False,
                    'error': 'Email already exists'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user,
                role=role,
                phone=request.data.get('phone', ''),
                address=request.data.get('address', ''),
                date_of_birth=request.data.get('date_of_birth')
            )
            
            # If student, create student profile
            if role == 'student':
                student_id = request.data.get('student_id')
                if not student_id:
                    # Generate student ID if not provided
                    student_id = generate_student_id()
                
                student_profile = StudentProfile.objects.create(
                    user=user,
                    student_id=student_id,
                    graduation_year=request.data.get('graduation_year'),
                    gpa=request.data.get('gpa'),
                    enrollment_status='active'
                )
            
            # Serialize and return user data
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
        
        # Get user profile
        try:
            profile = user.profile
        except UserProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get student profile if user is a student
        student_profile = None
        if profile.is_student:
            try:
                student_profile = user.student_profile
            except StudentProfile.DoesNotExist:
                pass
        
        # Serialize data
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
        
        with transaction.atomic():
            # Update user fields
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            if 'email' in request.data:
                user.email = request.data['email']
            user.save()
            
            # Update user profile
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
            
            # Serialize and return updated data
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
