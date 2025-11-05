"""
Add API endpoints for managing program requirements
"""

from django.core.management.base import BaseCommand
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from courses.models import Program, ProgramRequirement, ProgramCourseRequirement, Course, Department
from courses.serializers import ProgramRequirementSerializer, ProgramCourseRequirementSerializer
import re


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_program_requirements(request, program_id):
    """Get all requirements for a program"""
    try:
        program = Program.objects.get(id=program_id)
        requirements = program.requirements.all().order_by('order')
        
        serializer = ProgramRequirementSerializer(requirements, many=True)
        
        return Response({
            'success': True,
            'requirements': serializer.data
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
def create_program_requirement(request):
    """Create a new program requirement"""
    try:
        with transaction.atomic():
            requirement_data = request.data.copy()
            
            serializer = ProgramRequirementSerializer(data=requirement_data)
            if serializer.is_valid():
                requirement = serializer.save()
                
                # Handle course requirements if provided
                if 'courses' in request.data:
                    courses = request.data['courses']
                    for course_code in courses:
                        try:
                            # Parse course code (e.g., "CS230" -> "CS", "230")
                            match = re.match(r'^([A-Z]+)(\d+[A-Z]*)$', course_code)
                            if match:
                                dept_code = match.group(1)
                                course_num = match.group(2)
                                
                                department = Department.objects.get(code=dept_code)
                                course = Course.objects.get(department=department, course_number=course_num)
                                
                                ProgramCourseRequirement.objects.create(
                                    requirement=requirement,
                                    course=course,
                                    is_required=True
                                )
                        except (Department.DoesNotExist, Course.DoesNotExist):
                            pass  # Skip courses that don't exist
                
                return Response({
                    'success': True,
                    'message': 'Requirement created successfully',
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
@api_view(['PUT'])
@permission_classes([AllowAny])
def update_program_requirement(request, requirement_id):
    """Update an existing program requirement"""
    try:
        with transaction.atomic():
            requirement = ProgramRequirement.objects.get(id=requirement_id)
            requirement_data = request.data.copy()
            
            serializer = ProgramRequirementSerializer(requirement, data=requirement_data, partial=True)
            if serializer.is_valid():
                updated_requirement = serializer.save()
                
                # Handle course requirements if provided
                if 'courses' in request.data:
                    # Clear existing course requirements
                    requirement.course_requirements.all().delete()
                    
                    # Add new course requirements
                    courses = request.data['courses']
                    for course_code in courses:
                        try:
                            match = re.match(r'^([A-Z]+)(\d+[A-Z]*)$', course_code)
                            if match:
                                dept_code = match.group(1)
                                course_num = match.group(2)
                                
                                department = Department.objects.get(code=dept_code)
                                course = Course.objects.get(department=department, course_number=course_num)
                                
                                ProgramCourseRequirement.objects.create(
                                    requirement=updated_requirement,
                                    course=course,
                                    is_required=True
                                )
                        except (Department.DoesNotExist, Course.DoesNotExist):
                            pass
                
                return Response({
                    'success': True,
                    'message': 'Requirement updated successfully',
                    'requirement': ProgramRequirementSerializer(updated_requirement).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid requirement data',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
    except ProgramRequirement.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Requirement not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_program_requirement(request, requirement_id):
    """Delete a program requirement"""
    try:
        requirement = ProgramRequirement.objects.get(id=requirement_id)
        requirement.delete()
        
        return Response({
            'success': True,
            'message': 'Requirement deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except ProgramRequirement.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Requirement not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Command(BaseCommand):
    help = 'Add requirement management endpoints'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Requirement management endpoints are ready to be added to urls.py')
        )


