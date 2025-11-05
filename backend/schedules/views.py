from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import Schedule, ScheduleItem, DegreeAudit, UserCourseSelection
from .serializers import (
    ScheduleSerializer, ScheduleItemSerializer, ScheduleWithItemsSerializer,
    DegreeAuditSerializer, ScheduleOptimizationSerializer, UserCourseSelectionSerializer
)
from .services import ScheduleConflictDetector


class ScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for schedules"""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Schedule.objects.filter(student=self.request.user.student_profile)
        return Schedule.objects.none()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'list'] and self.request.query_params.get('with_items'):
            return ScheduleWithItemsSerializer
        return ScheduleSerializer
    
    def perform_create(self, serializer):
        if hasattr(self.request.user, 'student_profile'):
            serializer.save(student=self.request.user.student_profile)
    
    @action(detail=True, methods=['get'])
    def conflicts(self, request, pk=None):
        """Get conflicts for a specific schedule"""
        schedule = self.get_object()
        detector = ScheduleConflictDetector(schedule)
        conflicts = detector.detect_conflicts()
        
        return Response(conflicts)
    
    @action(detail=True, methods=['get'])
    def optimize(self, request, pk=None):
        """Get optimization suggestions for a schedule"""
        schedule = self.get_object()
        detector = ScheduleConflictDetector(schedule)
        optimization = detector.optimize_schedule()
        
        serializer = ScheduleOptimizationSerializer(optimization)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_course(self, request, pk=None):
        """Add a course to the schedule"""
        schedule = self.get_object()
        offering_id = request.data.get('offering_id')
        
        if not offering_id:
            return Response(
                {'error': 'offering_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from courses.models import CourseOffering
            offering = CourseOffering.objects.get(id=offering_id)
        except CourseOffering.DoesNotExist:
            return Response(
                {'error': 'Course offering not found'}, 
                status=status.HTTP_404_NOT_F
            )
        
        # Check for conflicts
        detector = ScheduleConflictDetector(schedule)
        can_add, conflicts = detector.can_add_course(offering)
        
        if not can_add:
            return Response({
                'error': 'Cannot add course due to conflicts',
                'conflicts': [conflict['description'] for conflict in conflicts]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create schedule item
        schedule_item = ScheduleItem.objects.create(
            schedule=schedule,
            offering=offering
        )
        
        serializer = ScheduleItemSerializer(schedule_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def remove_course(self, request, pk=None):
        """Remove a course from the schedule"""
        schedule = self.get_object()
        offering_id = request.data.get('offering_id')
        
        if not offering_id:
            return Response(
                {'error': 'offering_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            schedule_item = ScheduleItem.objects.get(
                schedule=schedule,
                offering_id=offering_id
            )
            schedule_item.delete()
            return Response({'message': 'Course removed from schedule'})
        except ScheduleItem.DoesNotExist:
            return Response(
                {'error': 'Course not found in schedule'}, 
                status=status.HTTP_404_NOT_F
            )
    
    @action(detail=True, methods=['get'])
    def alternatives(self, request, pk=None):
        """Get alternative offerings for a conflicting course"""
        schedule = self.get_object()
        offering_id = request.query_params.get('offering_id')
        
        if not offering_id:
            return Response(
                {'error': 'offering_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from courses.models import CourseOffering
            offering = CourseOffering.objects.get(id=offering_id)
        except CourseOffering.DoesNotExist:
            return Response(
                {'error': 'Course offering not found'}, 
                status=status.HTTP_404_NOT_F
            )
        
        detector = ScheduleConflictDetector(schedule)
        alternatives = detector.suggest_alternatives(offering)
        
        from courses.serializers import CourseOfferingSerializer
        serializer = CourseOfferingSerializer(alternatives, many=True)
        return Response(serializer.data)


class ScheduleItemViewSet(viewsets.ModelViewSet):
    """ViewSet for schedule items"""
    queryset = ScheduleItem.objects.all()
    serializer_class = ScheduleItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return ScheduleItem.objects.filter(
                schedule__student=self.request.user.student_profile
            )
        return ScheduleItem.objects.none()


class DegreeAuditViewSet(viewsets.ModelViewSet):
    """ViewSet for degree audits"""
    queryset = DegreeAudit.objects.all()
    serializer_class = DegreeAuditSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return DegreeAudit.objects.filter(student=self.request.user.student_profile)
        return DegreeAudit.objects.none()
    
    @action(detail=True, methods=['post'])
    def refresh(self, request, pk=None):
        """Refresh degree audit data"""
        audit = self.get_object()
        # The audit is automatically updated when accessed due to the model methods
        serializer = self.get_serializer(audit)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def enroll(self, request):
        """Enroll student in a degree program"""
        if not hasattr(request.user, 'student_profile'):
            return Response(
                {'error': 'User is not a student'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        degree_program_id = request.data.get('degree_program_id')
        if not degree_program_id:
            return Response(
                {'error': 'degree_program_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from courses.models import Program
            program = Program.objects.get(id=degree_program_id, is_active=True)
        except Program.DoesNotExist:
            return Response(
                {'error': 'Program not found'}, 
                status=status.HTTP_404_NOT_F
            )
        
        # Check if student is already enrolled in this program
        if DegreeAudit.objects.filter(
            student=request.user.student_profile,
            program=program
        ).exists():
            return Response(
                {'error': 'Already enrolled in this program'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create degree audit
        degree_audit = DegreeAudit.objects.create(
            student=request.user.student_profile,
            program=program
        )
        
        serializer = self.get_serializer(degree_audit)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def unenroll(self, request, pk=None):
        """Unenroll student from a degree program"""
        audit = self.get_object()
        audit.delete()
        return Response({'message': 'Successfully unenrolled from degree program'})


class UserCourseSelectionViewSet(viewsets.ModelViewSet):
    """ViewSet for user course selections"""
    queryset = UserCourseSelection.objects.all()
    serializer_class = UserCourseSelectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return UserCourseSelection.objects.filter(student=self.request.user.student_profile)
        return UserCourseSelection.objects.none()

    def perform_create(self, serializer):
        if hasattr(self.request.user, 'student_profile'):
            serializer.save(student=self.request.user.student_profile)

    @action(detail=False, methods=['get'])
    def by_degree_audit(self, request):
        """Get course selections for a specific degree audit"""
        degree_audit_id = request.query_params.get('degree_audit_id')
        if not degree_audit_id:
            return Response({'error': 'degree_audit_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            degree_audit = DegreeAudit.objects.get(id=degree_audit_id, student=request.user.student_profile)
            selections = UserCourseSelection.objects.filter(degree_audit=degree_audit)
            serializer = self.get_serializer(selections, many=True)
            return Response(serializer.data)
        except DegreeAudit.DoesNotExist:
            return Response({'error': 'Degree audit not found'}, status=status.HTTP_404_NOT_F)