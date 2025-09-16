from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import StudentProfile, StudentDegree, CompletedCourse
from .serializers import (
    UserSerializer, StudentProfileSerializer, StudentDegreeSerializer,
    CompletedCourseSerializer, StudentWithProfileSerializer
)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user profile"""
        serializer = StudentWithProfileSerializer(request.user)
        return Response(serializer.data)


class StudentProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for student profiles"""
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return StudentProfile.objects.filter(user=self.request.user)
        return StudentProfile.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def degrees(self, request, pk=None):
        """Get degrees for a student profile"""
        profile = self.get_object()
        degrees = profile.degrees.all()
        serializer = StudentDegreeSerializer(degrees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def completed_courses(self, request, pk=None):
        """Get completed courses for a student profile"""
        profile = self.get_object()
        courses = profile.completed_courses.all()
        serializer = CompletedCourseSerializer(courses, many=True)
        return Response(serializer.data)