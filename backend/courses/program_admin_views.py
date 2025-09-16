from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import (
    Program, ProgramType, ProgramRequirement, ProgramCourseRequirement, 
    ProgramConstraint, Department, Course
)
from .serializers import (
    ProgramSerializer, ProgramTypeSerializer, ProgramRequirementSerializer,
    ProgramCourseRequirementSerializer, ProgramConstraintSerializer,
    DepartmentSerializer, CourseSerializer
)
from .admin_views import is_admin


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def simple_admin_program_types(request):
    """Get all program types"""
    program_types = ProgramType.objects.all()
    serializer = ProgramTypeSerializer(program_types, many=True)
    
    return Response({
        'success': True,
        'program_types': serializer.data,
        'message': 'This is a test endpoint - no authentication required'
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def simple_admin_programs(request):
    """Get all programs"""
    programs = Program.objects.all().order_by('program_type', 'name')
    serializer = ProgramSerializer(programs, many=True)
    
    return Response({
        'success': True,
        'programs': serializer.data,
        'message': 'This is a test endpoint - no authentication required'
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def simple_admin_create_program(request):
    """Create a new program"""
    try:
        with transaction.atomic():
            program_data = request.data.copy()
            
            serializer = ProgramSerializer(data=program_data)
            if serializer.is_valid():
                program = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Program created successfully',
                    'program': ProgramSerializer(program).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid program data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['PUT'])
@permission_classes([AllowAny])
def simple_admin_update_program(request, program_id):
    """Update an existing program"""
    try:
        program = Program.objects.get(id=program_id)
        
        with transaction.atomic():
            program_data = request.data.copy()
            
            serializer = ProgramSerializer(program, data=program_data, partial=True)
            if serializer.is_valid():
                program = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Program updated successfully',
                    'program': ProgramSerializer(program).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid program data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Program.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def simple_admin_delete_program(request, program_id):
    """Delete a program"""
    try:
        program = Program.objects.get(id=program_id)
        program.delete()
        
        return Response({
            'success': True,
            'message': 'Program deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Program.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Program not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def simple_admin_create_program_requirement(request):
    """Create a new program requirement"""
    try:
        with transaction.atomic():
            requirement_data = request.data.copy()
            
            serializer = ProgramRequirementSerializer(data=requirement_data)
            if serializer.is_valid():
                requirement = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Program requirement created successfully',
                    'requirement': ProgramRequirementSerializer(requirement).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid requirement data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def simple_admin_create_program_course_requirement(request):
    """Create a new program course requirement"""
    try:
        with transaction.atomic():
            course_req_data = request.data.copy()
            
            serializer = ProgramCourseRequirementSerializer(data=course_req_data)
            if serializer.is_valid():
                course_req = serializer.save()
                
                return Response({
                    'success': True,
                    'message': 'Program course requirement created successfully',
                    'course_requirement': ProgramCourseRequirementSerializer(course_req).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid course requirement data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
