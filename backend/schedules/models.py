from django.db import models
from django.contrib.auth.models import User


class Schedule(models.Model):
    """Represents a student's schedule for a semester"""
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
    ]
    
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='schedules')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField()
    name = models.CharField(max_length=100, default='My Schedule')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'semester', 'year', 'name']
        ordering = ['-year', 'semester', 'name']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.semester.title()} {self.year} ({self.name})"
    
    @property
    def total_credits(self):
        """Calculate total credits in this schedule"""
        return sum(item.offering.course.credits for item in self.schedule_items.all())
    
    @property
    def has_conflicts(self):
        """Check if there are any time conflicts in this schedule"""
        return self.check_time_conflicts()
    
    def check_time_conflicts(self):
        """Check for time conflicts between courses in this schedule"""
        time_slots = []
        for item in self.schedule_items.all():
            for time_slot in item.offering.time_slots.all():
                time_slots.append({
                    'day': time_slot.day_of_week,
                    'start': time_slot.start_time,
                    'end': time_slot.end_time,
                    'course': item.offering.course.full_code
                })
        
        for i, slot1 in enumerate(time_slots):
            for j, slot2 in enumerate(time_slots[i+1:], i+1):
                if (slot1['day'] == slot2['day'] and 
                    not (slot1['end'] <= slot2['start'] or slot2['end'] <= slot1['start'])):
                    return True
        return False


class ScheduleItem(models.Model):
    """Represents a course in a student's schedule"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='schedule_items')
    offering = models.ForeignKey('courses.CourseOffering', on_delete=models.CASCADE, related_name='schedule_items')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['schedule', 'offering']
        ordering = ['offering__course__department__code', 'offering__course__course_number']
    
    def __str__(self):
        return f"{self.schedule} - {self.offering.course.full_code}"
    
    def clean(self):
        """Validate the schedule item"""
        from django.core.exceptions import ValidationError
        
        if (self.schedule.student.completed_courses
            .filter(course=self.offering.course, grade__in=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P'])
            .exists()):
            raise ValidationError(f"Student has already completed {self.offering.course.full_code}")
        
        if not self.check_prerequisites():
            raise ValidationError(f"Prerequisites not met for {self.offering.course.full_code}")
    
    def check_prerequisites(self):
        """Check if student meets all prerequisites for this course"""
        student = self.schedule.student
        course = self.offering.course
        
        prerequisites = course.prerequisites.all()
        
        for prereq in prerequisites:
            if not (student.completed_courses
                   .filter(course=prereq.prerequisite_course, 
                          grade__in=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P'])
                   .exists()):
                return False
        
        return True


class DegreeAudit(models.Model):
    """Tracks degree progress for a student"""
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='degree_audits')
    program = models.ForeignKey('courses.Program', on_delete=models.CASCADE, related_name='audits')
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'program']
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.program.name} Audit"
    
    def calculate_progress(self):
        """Calculate degree completion progress"""
        total_credits_required = self.program.total_credits_required
        
        course_selections = UserCourseSelection.objects.filter(degree_audit=self)
        completed_courses = course_selections.filter(status='completed')
        credits_earned = sum(
            float(selection.course.credits) for selection in completed_courses
        )
        
        student_completed_credits = self.student.total_credits_earned or 0
        total_credits_earned = max(credits_earned, student_completed_credits)
        
        return {
            'total_credits_required': total_credits_required,
            'credits_earned': total_credits_earned,
            'credits_remaining': float(total_credits_required) - total_credits_earned,
            'percentage_complete': (total_credits_earned / float(total_credits_required) * 100) if total_credits_required > 0 else 0,
            'course_selections_count': course_selections.count(),
            'completed_course_selections': completed_courses.count()
        }
    
    def get_requirement_status(self):
        """Get status of each degree requirement"""
        requirements_status = []
        
        for requirement in self.program.requirements.all():
            satisfied_courses = []
            for course_req in requirement.course_requirements.filter(is_required=True):
                if (self.student.completed_courses
                    .filter(course=course_req.course, 
                           grade__in=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P'])
                    .exists()):
                    satisfied_courses.append(course_req.course)
            
            credits_earned = sum(course.credits for course in satisfied_courses)
            credits_required = requirement.credits_required or 0
            
            requirements_status.append({
                'requirement': {
                    'id': requirement.id,
                    'name': requirement.name,
                    'requirement_type': requirement.requirement_type,
                    'description': requirement.description,
                    'credits_required': requirement.credits_required,
                },
                'credits_required': requirement.credits_required,
                'credits_earned': credits_earned,
                'is_satisfied': credits_earned >= credits_required,
                'satisfied_courses': [
                    {
                        'id': course.id,
                        'full_code': course.full_code,
                        'title': course.title,
                        'credits': course.credits,
                    }
                    for course in satisfied_courses
                ]
            })
        
        return requirements_status
    
    def get_cross_program_satisfaction(self):
        """Get courses that satisfy multiple programs for this student"""
        student_audits = DegreeAudit.objects.filter(student=self.student).exclude(id=self.id)
        cross_program_courses = []
        
        all_selections = UserCourseSelection.objects.filter(
            student=self.student,
            status='completed'
        )
        
        for selection in all_selections:
            other_programs_satisfied = []
            for audit in student_audits:
                if self._course_satisfies_program_requirements(selection.course, audit.program):
                    other_programs_satisfied.append(audit.program.name)
            
            if other_programs_satisfied:
                cross_program_courses.append({
                    'course': {
                        'id': selection.course.id,
                        'full_code': selection.course.full_code,
                        'title': selection.course.title,
                        'credits': selection.course.credits
                    },
                    'satisfies_programs': other_programs_satisfied,
                    'credits_shared': selection.course.credits
                })
        
        return cross_program_courses
    
    def _course_satisfies_program_requirements(self, course, program):
        """Check if a course satisfies requirements for a specific program"""
        for requirement in program.requirements.all():
            for course_req in requirement.course_requirements.filter(is_required=True):
                if course_req.course == course:
                    return True
        return False


class UserCourseSelection(models.Model):
    """Tracks courses selected by a student for their degree plan"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    student = models.ForeignKey('users.StudentProfile', on_delete=models.CASCADE, related_name='course_selections')
    degree_audit = models.ForeignKey(DegreeAudit, on_delete=models.CASCADE, related_name='course_selections')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='user_selections')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    grade = models.CharField(max_length=5, blank=True, null=True, help_text="Grade received (e.g., A+, A, B+)")
    semester_taken = models.CharField(max_length=20, blank=True, null=True, help_text="Semester when taken (e.g., Fall 2024)")
    timetable_box_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the timetable box this course belongs to")
    notes = models.TextField(blank=True, help_text="Additional notes about this course")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'course', 'degree_audit']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.full_code} ({self.status})"