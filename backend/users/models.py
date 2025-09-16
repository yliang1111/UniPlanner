from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser


class UserProfile(models.Model):
    """Extended profile for all users"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Administrator'),
        ('advisor', 'Academic Advisor'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.role})"
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_student(self):
        return self.role == 'student'


class StudentProfile(models.Model):
    """Extended profile for students"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    total_credits_earned = models.PositiveIntegerField(default=0)
    enrollment_status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('graduated', 'Graduated'),
            ('suspended', 'Suspended'),
        ],
        default='active'
    )
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"


class StudentDegree(models.Model):
    """Links students to their degree programs"""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='degrees')
    degree_program = models.ForeignKey('courses.DegreeProgram', on_delete=models.CASCADE, related_name='students')
    start_date = models.DateField()
    expected_graduation = models.DateField(null=True, blank=True)
    is_primary = models.BooleanField(default=True)  # For students with multiple degrees
    
    class Meta:
        unique_together = ['student', 'degree_program']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.degree_program.name}"


class CompletedCourse(models.Model):
    """Tracks courses completed by students"""
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D+', 'D+'),
        ('D', 'D'),
        ('D-', 'D-'),
        ('F', 'F'),
        ('P', 'Pass'),
        ('NP', 'No Pass'),
        ('W', 'Withdraw'),
        ('I', 'Incomplete'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='completed_courses')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='completed_by')
    semester = models.CharField(max_length=10)
    year = models.PositiveIntegerField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    credits_earned = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['student', 'course', 'semester', 'year']
        ordering = ['-year', 'semester', 'course__department__code', 'course__course_number']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.full_code} ({self.grade})"
    
    @property
    def is_passing(self):
        """Check if the grade is passing"""
        passing_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P']
        return self.grade in passing_grades