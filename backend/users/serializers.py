from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, StudentProfile, StudentDegree, CompletedCourse
from courses.serializers import CourseSerializer, DegreeProgramSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'role', 'phone', 'address', 
            'date_of_birth', 'created_at', 'updated_at'
        ]


class StudentDegreeSerializer(serializers.ModelSerializer):
    degree_program = DegreeProgramSerializer(read_only=True)
    degree_program_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = StudentDegree
        fields = [
            'id', 'student', 'degree_program', 'degree_program_id',
            'start_date', 'expected_graduation', 'is_primary'
        ]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    degrees = StudentDegreeSerializer(many=True, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'student_id', 'graduation_year',
            'gpa', 'total_credits_earned', 'enrollment_status', 'degrees'
        ]


class CompletedCourseSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    is_passing = serializers.ReadOnlyField()
    
    class Meta:
        model = CompletedCourse
        fields = [
            'id', 'student', 'course', 'course_id', 'semester',
            'year', 'grade', 'credits_earned', 'is_passing'
        ]


class StudentWithProfileSerializer(UserSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    degrees = StudentDegreeSerializer(many=True, read_only=True)
    completed_courses = CompletedCourseSerializer(many=True, read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + [
            'student_profile', 'degrees', 'completed_courses'
        ]
