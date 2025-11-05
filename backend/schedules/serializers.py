from rest_framework import serializers
from .models import Schedule, ScheduleItem, DegreeAudit, UserCourseSelection
from .services import ScheduleConflictDetector
from courses.serializers import CourseOfferingSerializer
from users.serializers import StudentProfileSerializer


class ScheduleSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    total_credits = serializers.ReadOnlyField()
    has_conflicts = serializers.ReadOnlyField()
    
    class Meta:
        model = Schedule
        fields = [
            'id', 'student', 'semester', 'year', 'name',
            'is_active', 'created_at', 'updated_at',
            'total_credits', 'has_conflicts'
        ]


class ScheduleItemSerializer(serializers.ModelSerializer):
    offering = CourseOfferingSerializer(read_only=True)
    offering_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ScheduleItem
        fields = ['id', 'schedule', 'offering', 'offering_id', 'added_at']
    
    def validate(self, data):
        """Validate schedule item before creation"""
        schedule = data['schedule']
        offering = data['offering']
        
        detector = ScheduleConflictDetector(schedule)
        can_add, conflicts = detector.can_add_course(offering)
        
        if not can_add:
            raise serializers.ValidationError({
                'conflicts': [conflict['description'] for conflict in conflicts]
            })
        
        return data


class ScheduleWithItemsSerializer(ScheduleSerializer):
    schedule_items = ScheduleItemSerializer(many=True, read_only=True)
    conflicts = serializers.SerializerMethodField()
    
    def get_conflicts(self, obj):
        """Get conflicts for this schedule"""
        detector = ScheduleConflictDetector(obj)
        return detector.detect_conflicts()
    
    class Meta(ScheduleSerializer.Meta):
        fields = ScheduleSerializer.Meta.fields + ['schedule_items', 'conflicts']


class DegreeAuditSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    program = serializers.StringRelatedField(read_only=True)
    progress = serializers.SerializerMethodField()
    requirement_status = serializers.SerializerMethodField()
    cross_program_satisfaction = serializers.SerializerMethodField()
    
    def get_progress(self, obj):
        """Get degree completion progress"""
        return obj.calculate_progress()
    
    def get_requirement_status(self, obj):
        """Get status of each degree requirement"""
        return obj.get_requirement_status()
    
    def get_cross_program_satisfaction(self, obj):
        """Get courses that satisfy multiple programs"""
        return obj.get_cross_program_satisfaction()
    
    class Meta:
        model = DegreeAudit
        fields = [
            'id', 'student', 'program', 'last_updated',
            'progress', 'requirement_status', 'cross_program_satisfaction'
        ]


class UserCourseSelectionSerializer(serializers.ModelSerializer):
    course_details = serializers.SerializerMethodField()
    student = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = UserCourseSelection
        fields = [
            'id', 'student', 'degree_audit', 'course', 'course_details', 'status', 'grade', 
            'semester_taken', 'timetable_box_id', 'notes', 'added_at', 'updated_at'
        ]
    
    def get_course_details(self, obj):
        return {
            'id': obj.course.id,
            'full_code': obj.course.full_code,
            'title': obj.course.title,
            'credits': obj.course.credits,
            'department': obj.course.department.code
        }


class ScheduleOptimizationSerializer(serializers.Serializer):
    """Serializer for schedule optimization suggestions"""
    conflicts = serializers.ListField()
    gaps = serializers.ListField()
    workload = serializers.DictField()
    recommendations = serializers.ListField()

