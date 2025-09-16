from rest_framework import serializers
from .models import Schedule, ScheduleItem, DegreeAudit
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
        
        # Check for conflicts
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
    degree_program = serializers.StringRelatedField(read_only=True)
    progress = serializers.SerializerMethodField()
    requirement_status = serializers.SerializerMethodField()
    
    def get_progress(self, obj):
        """Get degree completion progress"""
        return obj.calculate_progress()
    
    def get_requirement_status(self, obj):
        """Get status of each degree requirement"""
        return obj.get_requirement_status()
    
    class Meta:
        model = DegreeAudit
        fields = [
            'id', 'student', 'degree_program', 'last_updated',
            'progress', 'requirement_status'
        ]


class ScheduleOptimizationSerializer(serializers.Serializer):
    """Serializer for schedule optimization suggestions"""
    conflicts = serializers.ListField()
    gaps = serializers.ListField()
    workload = serializers.DictField()
    recommendations = serializers.ListField()

