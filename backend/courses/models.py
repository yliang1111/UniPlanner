from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    """Represents a university department"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """Represents a university course"""
    TERM_CHOICES = [
        ('fall', 'Fall'),
        ('winter', 'Winter'),
        ('spring', 'Spring'),
    ]
    
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    course_number = models.CharField(max_length=10)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.DecimalField(max_digits=3, decimal_places=2)
    is_active = models.BooleanField(default=True)
    terms_offered = models.JSONField(default=list, help_text="List of terms when course is offered (fall, winter, spring)")
    
    # Additional course management fields
    corequisites = models.ManyToManyField('self', blank=True, symmetrical=True, related_name='corequisite_for')
    antirequisites = models.ManyToManyField('self', blank=True, symmetrical=True, related_name='antirequisite_for')
    restricted_to_majors = models.ManyToManyField('DegreeProgram', blank=True, related_name='restricted_courses')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_courses')
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_courses')
    
    class Meta:
        unique_together = ['department', 'course_number']
        ordering = ['department__code', 'course_number']
    
    def __str__(self):
        return f"{self.department.code} {self.course_number} - {self.title}"
    
    @property
    def full_code(self):
        return f"{self.department.code} {self.course_number}"
    
    def get_prerequisites(self):
        """Get all prerequisite courses"""
        return [prereq.prerequisite_course for prereq in self.prerequisites.all()]
    
    def get_prerequisite_groups(self):
        """Get all prerequisite groups with their courses"""
        groups = []
        for group in self.prerequisite_groups.all():
            group_data = {
                'id': group.id,
                'name': group.name,
                'description': group.description,
                'is_required': group.is_required,
                'courses': [prereq.prerequisite_course for prereq in group.prerequisites.all()]
            }
            groups.append(group_data)
        return groups
    
    def get_corequisites(self):
        """Get all corequisite courses"""
        return self.corequisites.all()
    
    def get_antirequisites(self):
        """Get all antirequisite courses"""
        return self.antirequisites.all()
    
    def get_restricted_majors(self):
        """Get all majors this course is restricted to"""
        return self.restricted_to_majors.all()


class PrerequisiteGroup(models.Model):
    """Represents a group of prerequisite courses where one must be satisfied"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisite_groups')
    name = models.CharField(max_length=100, help_text="Name for this prerequisite group (e.g., 'Statistics Requirement')")
    description = models.TextField(blank=True, help_text="Description of what this group represents")
    is_required = models.BooleanField(default=True, help_text="Whether this group is required or optional")
    
    class Meta:
        ordering = ['course', 'name']
    
    def __str__(self):
        return f"{self.course.full_code} - {self.name}"


class Prerequisite(models.Model):
    """Represents prerequisite relationships between courses"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='required_for')
    group = models.ForeignKey(PrerequisiteGroup, on_delete=models.CASCADE, related_name='prerequisites', null=True, blank=True)
    
    class Meta:
        unique_together = ['course', 'prerequisite_course']
    
    def __str__(self):
        if self.group:
            return f"{self.prerequisite_course.full_code} → {self.course.full_code} (in {self.group.name})"
        return f"{self.prerequisite_course.full_code} → {self.course.full_code}"


class DegreeProgram(models.Model):
    """Represents a degree program (e.g., Computer Science BS)"""
    name = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='degree_programs')
    total_credits_required = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.department.code})"


class DegreeRequirement(models.Model):
    """Represents requirements for a degree program"""
    REQUIREMENT_TYPES = [
        ('core', 'Core Course'),
        ('elective', 'Elective'),
        ('general_ed', 'General Education'),
        ('major', 'Major Requirement'),
        ('minor', 'Minor Requirement'),
    ]
    
    degree_program = models.ForeignKey(DegreeProgram, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(max_length=20, choices=REQUIREMENT_TYPES)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits_required = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.degree_program.name} - {self.name}"


class CourseRequirement(models.Model):
    """Links specific courses to degree requirements"""
    requirement = models.ForeignKey(DegreeRequirement, on_delete=models.CASCADE, related_name='course_requirements')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='degree_requirements')
    is_required = models.BooleanField(default=True)  # False for elective options
    
    class Meta:
        unique_together = ['requirement', 'course']
    
    def __str__(self):
        return f"{self.requirement.name} - {self.course.full_code}"


class CourseOffering(models.Model):
    """Represents a specific offering of a course in a semester"""
    SEMESTER_CHOICES = [
        ('fall', 'Fall'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('winter', 'Winter'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    year = models.PositiveIntegerField()
    section = models.CharField(max_length=10, default='001')
    instructor = models.CharField(max_length=100, blank=True)
    capacity = models.PositiveIntegerField()
    enrolled = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['course', 'semester', 'year', 'section']
        ordering = ['year', 'semester', 'course__department__code', 'course__course_number']
    
    def __str__(self):
        return f"{self.course.full_code} - {self.semester.title()} {self.year} ({self.section})"
    
    @property
    def is_available(self):
        return self.enrolled < self.capacity


class TimeSlot(models.Model):
    """Represents a time slot for a course offering"""
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]
    
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name='time_slots')
    day_of_week = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.offering} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ProgramType(models.Model):
    """Represents types of programs (Major, Minor, Joint Major, etc.)"""
    PROGRAM_TYPE_CHOICES = [
        ('major', 'Major'),
        ('minor', 'Minor'),
        ('joint_major', 'Joint Major'),
        ('honours', 'Honours'),
        ('specialization', 'Specialization'),
    ]
    
    name = models.CharField(max_length=50, choices=PROGRAM_TYPE_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.display_name


class Program(models.Model):
    """Represents an academic program (e.g., Mathematics Major, Computer Science Minor)"""
    name = models.CharField(max_length=200, unique=True)
    program_type = models.ForeignKey(ProgramType, on_delete=models.CASCADE, related_name='programs')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs', null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    
    # Academic requirements
    minimum_overall_average = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Minimum overall average required")
    minimum_major_average = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Minimum major average required")
    total_credits_required = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    
    # Additional requirements
    co_op_available = models.BooleanField(default=False)
    honours_available = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['program_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.program_type.display_name})"


class ProgramRequirement(models.Model):
    """Represents a requirement within a program (e.g., Required Courses, Electives)"""
    REQUIREMENT_TYPE_CHOICES = [
        ('required_courses', 'Required Courses'),
        ('elective_courses', 'Elective Courses'),
        ('credit_requirement', 'Credit Requirement'),
        ('average_requirement', 'Average Requirement'),
        ('course_group', 'Course Group'),
        ('subject_requirement', 'Subject Requirement'),
        ('level_requirement', 'Level Requirement'),
    ]
    
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements')
    name = models.CharField(max_length=200)
    requirement_type = models.CharField(max_length=50, choices=REQUIREMENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Requirements
    credits_required = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    courses_required = models.PositiveIntegerField(null=True, blank=True)
    minimum_level = models.PositiveIntegerField(null=True, blank=True, help_text="Minimum course level (e.g., 200, 300, 400)")
    maximum_courses = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum courses from same subject")
    
    # Constraints
    subject_codes = models.JSONField(default=list, blank=True, help_text="Allowed subject codes")
    excluded_subject_codes = models.JSONField(default=list, blank=True, help_text="Excluded subject codes")
    require_different_subjects = models.BooleanField(default=False, help_text="Require courses from different subjects")
    minimum_subjects = models.PositiveIntegerField(default=1, help_text="Minimum number of different subjects")
    
    # Ordering and grouping
    order = models.PositiveIntegerField(default=0)
    parent_requirement = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='sub_requirements')
    
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['program', 'order', 'name']
    
    def __str__(self):
        return f"{self.program.name} - {self.name}"


class ProgramCourseRequirement(models.Model):
    """Links courses to program requirements"""
    requirement = models.ForeignKey(ProgramRequirement, on_delete=models.CASCADE, related_name='course_requirements')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='program_requirements')
    
    # Course selection rules
    is_required = models.BooleanField(default=True, help_text="Whether this specific course is required")
    is_alternative = models.BooleanField(default=False, help_text="Whether this is an alternative to other courses")
    alternative_group = models.CharField(max_length=100, blank=True, help_text="Group name for alternative courses")
    
    # Constraints
    minimum_grade = models.CharField(max_length=5, blank=True, help_text="Minimum grade required")
    maximum_credits = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        unique_together = ['requirement', 'course']
        ordering = ['requirement', 'order', 'course']
    
    def __str__(self):
        return f"{self.requirement.name} - {self.course.full_code}"


class ProgramConstraint(models.Model):
    """Represents additional constraints for programs"""
    CONSTRAINT_TYPE_CHOICES = [
        ('substitution', 'Course Substitution'),
        ('exclusion', 'Course Exclusion'),
        ('prerequisite_override', 'Prerequisite Override'),
        ('credit_limit', 'Credit Limit'),
        ('cross_listing', 'Cross-listing Restriction'),
    ]
    
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='constraints')
    constraint_type = models.CharField(max_length=50, choices=CONSTRAINT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Constraint details
    affected_courses = models.JSONField(default=list, help_text="List of course IDs affected")
    conditions = models.JSONField(default=dict, help_text="Conditions for the constraint")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['program', 'constraint_type', 'name']
    
    def __str__(self):
        return f"{self.program.name} - {self.name}"