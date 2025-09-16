from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, F
from .models import (
    Department, Course, Prerequisite, DegreeProgram, DegreeRequirement,
    CourseRequirement, CourseOffering, TimeSlot
)
from .serializers import (
    DepartmentSerializer, CourseSerializer, PrerequisiteSerializer,
    DegreeProgramSerializer, DegreeRequirementSerializer,
    CourseRequirementSerializer, CourseOfferingSerializer,
    CourseWithPrerequisitesSerializer, CourseRecommendationSerializer
)
from .services import PrerequisiteValidator


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for courses"""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    
    def get_serializer_class(self):
        if self.action == 'list' and self.request.query_params.get('with_prerequisites'):
            return CourseWithPrerequisitesSerializer
        return CourseSerializer
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__code=department)
        
        # Filter by course number
        course_number = self.request.query_params.get('course_number')
        if course_number:
            queryset = queryset.filter(course_number__icontains=course_number)
        
        # Filter by title
        title = self.request.query_params.get('title')
        if title:
            queryset = queryset.filter(title__icontains=title)
        
        # Filter by credits
        min_credits = self.request.query_params.get('min_credits')
        max_credits = self.request.query_params.get('max_credits')
        if min_credits:
            queryset = queryset.filter(credits__gte=min_credits)
        if max_credits:
            queryset = queryset.filter(credits__lte=max_credits)
        
        return queryset
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def available(self, request):
        """Get courses available to the current student (prerequisites satisfied)"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'User is not a student'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validator = PrerequisiteValidator(request.user.student_profile)
        available_courses = validator.get_available_courses()
        
        serializer = CourseWithPrerequisitesSerializer(
            available_courses, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def recommendations(self, request):
        """Get course recommendations for the current student"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'User is not a student'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validator = PrerequisiteValidator(request.user.student_profile)
        target_course_id = request.query_params.get('target_course')
        
        if target_course_id:
            try:
                target_course = Course.objects.get(id=target_course_id)
                recommendations = validator.get_recommended_course_sequence(target_course)
            except Course.DoesNotExist:
                return Response(
                    {'error': 'Target course not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            recommendations = validator.get_recommended_course_sequence()
        
        serializer = CourseRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def prerequisite_chain(self, request, pk=None):
        """Get the complete prerequisite chain for a course"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'User is not a student'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course = self.get_object()
        validator = PrerequisiteValidator(request.user.student_profile)
        chain = validator.get_prerequisite_chain(course)
        
        return Response(chain)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def can_take(self, request, pk=None):
        """Check if student can take this course"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'User is not a student'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        course = self.get_object()
        validator = PrerequisiteValidator(request.user.student_profile)
        can_take, missing_prerequisites = validator.can_take_course(course)
        
        return Response({
            'can_take': can_take,
            'missing_prerequisites': missing_prerequisites
        })


class PrerequisiteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for prerequisites"""
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteSerializer
    
    def get_queryset(self):
        queryset = Prerequisite.objects.all()
        
        # Filter by course
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by prerequisite course
        prereq_course_id = self.request.query_params.get('prerequisite_course')
        if prereq_course_id:
            queryset = queryset.filter(prerequisite_course_id=prereq_course_id)
        
        return queryset


class DegreeProgramViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for degree programs"""
    queryset = DegreeProgram.objects.filter(is_active=True)
    serializer_class = DegreeProgramSerializer
    
    def get_queryset(self):
        queryset = DegreeProgram.objects.filter(is_active=True)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__code=department)
        
        return queryset


class DegreeRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for degree requirements"""
    queryset = DegreeRequirement.objects.all()
    serializer_class = DegreeRequirementSerializer
    
    def get_queryset(self):
        queryset = DegreeRequirement.objects.all()
        
        # Filter by degree program
        degree_program_id = self.request.query_params.get('degree_program')
        if degree_program_id:
            queryset = queryset.filter(degree_program_id=degree_program_id)
        
        # Filter by requirement type
        requirement_type = self.request.query_params.get('requirement_type')
        if requirement_type:
            queryset = queryset.filter(requirement_type=requirement_type)
        
        return queryset


class CourseRequirementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for course requirements"""
    queryset = CourseRequirement.objects.all()
    serializer_class = CourseRequirementSerializer
    
    def get_queryset(self):
        queryset = CourseRequirement.objects.all()
        
        # Filter by requirement
        requirement_id = self.request.query_params.get('requirement')
        if requirement_id:
            queryset = queryset.filter(requirement_id=requirement_id)
        
        # Filter by course
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        return queryset


class CourseOfferingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for course offerings"""
    queryset = CourseOffering.objects.all()
    serializer_class = CourseOfferingSerializer
    
    def get_queryset(self):
        queryset = CourseOffering.objects.all()
        
        # Filter by course
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Filter by semester
        semester = self.request.query_params.get('semester')
        if semester:
            queryset = queryset.filter(semester=semester)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        
        # Filter by availability
        available_only = self.request.query_params.get('available_only')
        if available_only and available_only.lower() == 'true':
            queryset = queryset.filter(enrolled__lt=F('capacity'))
        
        return queryset