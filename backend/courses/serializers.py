from rest_framework import serializers
from .models import (
    Department, Course, Prerequisite, DegreeProgram, DegreeRequirement,
    CourseRequirement, CourseOffering, TimeSlot, ProgramType, Program, 
    ProgramRequirement, ProgramCourseRequirement, ProgramConstraint
)
from .services import PrerequisiteValidator


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'code', 'name']


class DegreeProgramSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DegreeProgram
        fields = [
            'id', 'name', 'department', 'department_id', 'total_credits_required',
            'description', 'is_active'
        ]


class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    full_code = serializers.ReadOnlyField()
    prerequisites = serializers.SerializerMethodField()
    prerequisite_groups = serializers.SerializerMethodField()
    corequisites = serializers.SerializerMethodField()
    antirequisites = serializers.SerializerMethodField()
    restricted_to_majors = DegreeProgramSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)
    last_modified_by = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'department', 'department_id', 'course_number', 'title',
            'description', 'credits', 'is_active', 'terms_offered', 'full_code', 
            'prerequisites', 'prerequisite_groups', 'corequisites', 'antirequisites', 
            'restricted_to_majors', 'created_by', 'last_modified', 'last_modified_by'
        ]
    
    def get_prerequisites(self, obj):
        """Get prerequisite courses"""
        return [{'id': prereq.id, 'full_code': prereq.full_code, 'title': prereq.title} for prereq in obj.get_prerequisites()]
    
    def get_prerequisite_groups(self, obj):
        """Get prerequisite groups"""
        groups = obj.get_prerequisite_groups()
        for group in groups:
            group['courses'] = [{'id': course.id, 'full_code': course.full_code, 'title': course.title} for course in group['courses']]
        return groups
    
    def get_corequisites(self, obj):
        """Get corequisite courses"""
        return [{'id': coreq.id, 'full_code': coreq.full_code, 'title': coreq.title} for coreq in obj.get_corequisites()]
    
    def get_antirequisites(self, obj):
        """Get antirequisite courses"""
        return [{'id': antireq.id, 'full_code': antireq.full_code, 'title': antireq.title} for antireq in obj.get_antirequisites()]


class PrerequisiteSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    prerequisite_course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    prerequisite_course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Prerequisite
        fields = [
            'id', 'course', 'course_id', 'prerequisite_course', 'prerequisite_course_id'
        ]


class ProgramTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramType
        fields = ['id', 'name', 'display_name', 'description']


class ProgramSerializer(serializers.ModelSerializer):
    program_type = ProgramTypeSerializer(read_only=True)
    program_type_id = serializers.IntegerField(write_only=True)
    department = DepartmentSerializer(read_only=True)
    department_id = serializers.IntegerField(write_only=True)
    requirements = serializers.SerializerMethodField()
    constraints = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = [
            'id', 'name', 'program_type', 'program_type_id', 'department', 'department_id',
            'code', 'description', 'minimum_overall_average', 'minimum_major_average',
            'total_credits_required', 'co_op_available', 'honours_available',
            'is_active', 'created_at', 'updated_at', 'requirements', 'constraints'
        ]

    def get_requirements(self, obj):
        return ProgramRequirementSerializer(obj.requirements.all(), many=True).data

    def get_constraints(self, obj):
        return ProgramConstraintSerializer(obj.constraints.all(), many=True).data


class ProgramRequirementSerializer(serializers.ModelSerializer):
    course_requirements = serializers.SerializerMethodField()
    sub_requirements = serializers.SerializerMethodField()
    program_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProgramRequirement
        fields = [
            'id', 'program_id', 'name', 'requirement_type', 'description', 'credits_required',
            'courses_required', 'minimum_level', 'maximum_courses', 'subject_codes',
            'excluded_subject_codes', 'require_different_subjects', 'minimum_subjects',
            'order', 'parent_requirement', 'is_required', 'is_active', 'course_requirements',
            'sub_requirements'
        ]

    def create(self, validated_data):
        program_id = validated_data.pop('program_id')
        program = Program.objects.get(id=program_id)
        validated_data['program'] = program
        return super().create(validated_data)

    def get_course_requirements(self, obj):
        return ProgramCourseRequirementSerializer(obj.course_requirements.all(), many=True).data

    def get_sub_requirements(self, obj):
        return ProgramRequirementSerializer(obj.sub_requirements.all(), many=True).data


class ProgramCourseRequirementSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProgramCourseRequirement
        fields = [
            'id', 'course', 'course_id', 'is_required', 'is_alternative',
            'alternative_group', 'minimum_grade', 'maximum_credits', 'order'
        ]


class ProgramConstraintSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramConstraint
        fields = [
            'id', 'constraint_type', 'name', 'description', 'affected_courses',
            'conditions', 'is_active'
        ]


class DegreeRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = DegreeRequirement
        fields = [
            'id', 'degree_program', 'requirement_type', 'name',
            'description', 'credits_required'
        ]


class CourseRequirementSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CourseRequirement
        fields = ['id', 'requirement', 'course', 'course_id', 'is_required']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'day_of_week', 'start_time', 'end_time', 'location'
        ]


class CourseOfferingSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.IntegerField(write_only=True)
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = CourseOffering
        fields = [
            'id', 'course', 'course_id', 'semester', 'year', 'section',
            'instructor', 'capacity', 'enrolled', 'is_available', 'time_slots'
        ]


class CourseWithPrerequisitesSerializer(CourseSerializer):
    prerequisites = PrerequisiteSerializer(many=True, read_only=True)
    can_take = serializers.SerializerMethodField()
    missing_prerequisites = serializers.SerializerMethodField()
    
    def get_can_take(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            validator = PrerequisiteValidator(request.user.student_profile)
            can_take, _ = validator.can_take_course(obj)
            return can_take
        return False
    
    def get_missing_prerequisites(self, obj):
        request = self.context.get('request')
        if request and hasattr(request.user, 'student_profile'):
            validator = PrerequisiteValidator(request.user.student_profile)
            _, missing = validator.can_take_course(obj)
            return missing
        return []
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + [
            'prerequisites', 'can_take', 'missing_prerequisites'
        ]


class CourseRecommendationSerializer(serializers.Serializer):
    course = CourseSerializer(read_only=True)
    can_take = serializers.BooleanField()
    missing_prerequisites = serializers.ListField(child=serializers.CharField())
    credits = serializers.IntegerField()
    priority = serializers.FloatField(required=False)
    reason = serializers.CharField(required=False)
    path_position = serializers.IntegerField(required=False)
