from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db import transaction
from .models import Course, Department, DegreeProgram, Prerequisite
from .serializers import CourseSerializer, DepartmentSerializer, DegreeProgramSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def simple_admin_courses(request):
    """Simple admin courses endpoint for testing"""
    # Get pagination parameters
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))  # Default 50 courses per page
    department_filter = request.GET.get('department', '')
    
    # Build optimized query
    courses_query = Course.objects.select_related('department').prefetch_related(
        'prerequisites__prerequisite_course__department',
        'prerequisite_groups',
        'corequisites__department',
        'antirequisites__department',
        'restricted_to_majors'
    ).order_by('department__code', 'course_number')
    
    # Apply department filter if provided
    if department_filter:
        courses_query = courses_query.filter(department__code=department_filter)
    
    # Get total count
    total_count = courses_query.count()
    
    # Apply pagination
    start = (page - 1) * page_size
    end = start + page_size
    courses = courses_query[start:end]
    
    serializer = CourseSerializer(courses, many=True)
    
    return Response({
        'success': True,
        'courses': serializer.data,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_count': total_count,
            'total_pages': (total_count + page_size - 1) // page_size
        },
        'message': 'This is a test endpoint - no authentication required'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def simple_admin_departments(request):
    """Simple admin departments endpoint for testing"""
    departments = Department.objects.all()
    serializer = DepartmentSerializer(departments, many=True)
    
    return Response({
        'success': True,
        'departments': serializer.data,
        'message': 'This is a test endpoint - no authentication required'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def simple_admin_degree_programs(request):
    """Simple admin degree programs endpoint for testing"""
    degree_programs = DegreeProgram.objects.all()
    serializer = DegreeProgramSerializer(degree_programs, many=True)
    
    return Response({
        'success': True,
        'degree_programs': serializer.data,
        'message': 'This is a test endpoint - no authentication required'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def simple_admin_create_course(request):
    """Simple admin course creation endpoint for testing"""
    try:
        with transaction.atomic():
            # Create course
            course_data = request.data.copy()
            
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

@api_view(['DELETE'])
@permission_classes([AllowAny])
def simple_admin_delete_course(request, course_id):
    """Simple admin course deletion endpoint for testing"""
    try:
        course = Course.objects.get(id=course_id)
        course.delete()
        
        return Response({
            'success': True,
            'message': 'Course deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Course.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Course not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def simple_admin_update_course(request, course_id):
    """Simple admin course update endpoint for testing"""
    try:
        course = Course.objects.get(id=course_id)
        
        with transaction.atomic():
            # Update course fields
            course_data = request.data.copy()
            
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
                
    except Course.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Course not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

