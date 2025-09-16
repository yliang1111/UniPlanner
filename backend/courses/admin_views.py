from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Department, DegreeProgram, Prerequisite
from .serializers import CourseSerializer, DepartmentSerializer, DegreeProgramSerializer
from users.models import UserProfile


def is_admin(user):
    """Check if user is an admin (excluding guest users)"""
    try:
        return user.profile.is_admin and user.username != 'guest'
    except:
        return False


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_courses_list(request):
    """Get all courses for admin management"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    courses = Course.objects.all().order_by('department__code', 'course_number')
    serializer = CourseSerializer(courses, many=True)
    
    return Response({
        'success': True,
        'courses': serializer.data
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_course(request):
    """Create a new course"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        with transaction.atomic():
            # Create course
            course_data = request.data.copy()
            course_data['created_by'] = request.user.id
            course_data['last_modified_by'] = request.user.id
            
            serializer = CourseSerializer(data=course_data)
            if serializer.is_valid():
                course = serializer.save()
                
                # Handle prerequisites
                if 'prerequisites' in request.data:
                    prerequisites = request.data['prerequisites']
                    for prereq_id in prerequisites:
                        try:
                            prereq_course = Course.objects.get(id=prereq_id)
                            Prerequisite.objects.get_or_create(
                                course=course,
                                prerequisite_course=prereq_course
                            )
                        except Course.DoesNotExist:
                            pass
                
                # Handle corequisites
                if 'corequisites' in request.data:
                    corequisites = request.data['corequisites']
                    course.corequisites.set(corequisites)
                
                # Handle antirequisites
                if 'antirequisites' in request.data:
                    antirequisites = request.data['antirequisites']
                    course.antirequisites.set(antirequisites)
                
                # Handle restricted majors
                if 'restricted_to_majors' in request.data:
                    majors = request.data['restricted_to_majors']
                    course.restricted_to_majors.set(majors)
                
                return Response({
                    'success': True,
                    'message': 'Course created successfully',
                    'course': CourseSerializer(course).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid course data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_update_course(request, course_id):
    """Update an existing course"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = get_object_or_404(Course, id=course_id)
        
        with transaction.atomic():
            # Update course fields
            course_data = request.data.copy()
            course_data['last_modified_by'] = request.user.id
            
            serializer = CourseSerializer(course, data=course_data, partial=True)
            if serializer.is_valid():
                course = serializer.save()
                
                # Handle prerequisites
                if 'prerequisites' in request.data:
                    # Clear existing prerequisites
                    course.prerequisites.all().delete()
                    
                    # Add new prerequisites
                    prerequisites = request.data['prerequisites']
                    for prereq_id in prerequisites:
                        try:
                            prereq_course = Course.objects.get(id=prereq_id)
                            Prerequisite.objects.get_or_create(
                                course=course,
                                prerequisite_course=prereq_course
                            )
                        except Course.DoesNotExist:
                            pass
                
                # Handle corequisites
                if 'corequisites' in request.data:
                    corequisites = request.data['corequisites']
                    course.corequisites.set(corequisites)
                
                # Handle antirequisites
                if 'antirequisites' in request.data:
                    antirequisites = request.data['antirequisites']
                    course.antirequisites.set(antirequisites)
                
                # Handle restricted majors
                if 'restricted_to_majors' in request.data:
                    majors = request.data['restricted_to_majors']
                    course.restricted_to_majors.set(majors)
                
                return Response({
                    'success': True,
                    'message': 'Course updated successfully',
                    'course': CourseSerializer(course).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid course data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_course(request, course_id):
    """Delete a course"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        course = get_object_or_404(Course, id=course_id)
        course.delete()
        
        return Response({
            'success': True,
            'message': 'Course deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_departments_list(request):
    """Get all departments for admin management"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    departments = Department.objects.all().order_by('code')
    serializer = DepartmentSerializer(departments, many=True)
    
    return Response({
        'success': True,
        'departments': serializer.data
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_degree_programs_list(request):
    """Get all degree programs for admin management"""
    if not is_admin(request.user):
        return Response({
            'success': False,
            'error': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    degree_programs = DegreeProgram.objects.all().order_by('name')
    serializer = DegreeProgramSerializer(degree_programs, many=True)
    
    return Response({
        'success': True,
        'degree_programs': serializer.data
    }, status=status.HTTP_200_OK)
