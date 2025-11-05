"""
Django Admin Configuration for Courses App

This module provides comprehensive admin interfaces for all course-related models
with advanced filtering, searching, and organization features.

Key Features:
- Department-based filtering for courses
- Advanced search capabilities
- Organized fieldsets for better data entry
- Filter horizontal widgets for many-to-many relationships
- Optimized queries with select_related for performance
"""

from django.contrib import admin
from .models import (
    Department, Course, Prerequisite, PrerequisiteGroup, DegreeProgram, 
    DegreeRequirement, CourseRequirement, CourseOffering, TimeSlot,
    ProgramType, Program, ProgramRequirement, ProgramCourseRequirement, ProgramConstraint
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['full_code', 'title', 'department', 'credits', 'is_active']
    list_filter = ['department', 'is_active', 'terms_offered']
    search_fields = ['course_number', 'title', 'department__code', 'department__name']
    ordering = ['department__code', 'course_number']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('department', 'course_number', 'title', 'description', 'credits')
        }),
        ('Availability', {
            'fields': ('is_active', 'terms_offered')
        }),
        ('Relationships', {
            'fields': ('corequisites', 'antirequisites', 'restricted_to_majors'),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': ('created_by', 'last_modified', 'last_modified_by'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ['corequisites', 'antirequisites', 'restricted_to_majors']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')


@admin.register(Prerequisite)
class PrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['prerequisite_course', 'course', 'group']
    list_filter = ['course__department', 'prerequisite_course__department']
    search_fields = ['course__title', 'prerequisite_course__title']
    ordering = ['course__department__code', 'course__course_number']


@admin.register(PrerequisiteGroup)
class PrerequisiteGroupAdmin(admin.ModelAdmin):
    list_display = ['course', 'name', 'is_required']
    list_filter = ['course__department', 'is_required']
    search_fields = ['course__title', 'name']
    ordering = ['course__department__code', 'course__course_number']


@admin.register(DegreeProgram)
class DegreeProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'total_credits_required', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['name', 'department__code', 'department__name']
    ordering = ['department__code', 'name']


@admin.register(DegreeRequirement)
class DegreeRequirementAdmin(admin.ModelAdmin):
    list_display = ['name', 'degree_program', 'requirement_type', 'credits_required']
    list_filter = ['degree_program__department', 'requirement_type']
    search_fields = ['name', 'degree_program__name']
    ordering = ['degree_program__department__code', 'degree_program__name', 'name']


@admin.register(CourseRequirement)
class CourseRequirementAdmin(admin.ModelAdmin):
    list_display = ['course', 'requirement', 'is_required']
    list_filter = ['course__department', 'requirement__degree_program__department', 'is_required']
    search_fields = ['course__title', 'requirement__name']
    ordering = ['requirement__degree_program__department__code', 'requirement__name', 'course__department__code']


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ['course', 'semester', 'year', 'section', 'instructor', 'capacity', 'enrolled']
    list_filter = ['course__department', 'semester', 'year']
    search_fields = ['course__title', 'instructor']
    ordering = ['-year', 'semester', 'course__department__code', 'course__course_number']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['offering', 'day_of_week', 'start_time', 'end_time', 'location']
    list_filter = ['offering__course__department', 'day_of_week']
    search_fields = ['offering__course__title', 'location']
    ordering = ['offering__course__department__code', 'day_of_week', 'start_time']


@admin.register(ProgramType)
class ProgramTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name']
    search_fields = ['name', 'display_name']
    ordering = ['name']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'program_type', 'department', 'code', 'is_active']
    list_filter = ['program_type', 'department', 'is_active']
    search_fields = ['name', 'code', 'department__code', 'department__name']
    ordering = ['program_type__name', 'department__code', 'name']


@admin.register(ProgramRequirement)
class ProgramRequirementAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'requirement_type', 'credits_required', 'is_required']
    list_filter = ['program__department', 'requirement_type', 'is_required']
    search_fields = ['name', 'program__name']
    ordering = ['program__department__code', 'program__name', 'name']


@admin.register(ProgramCourseRequirement)
class ProgramCourseRequirementAdmin(admin.ModelAdmin):
    list_display = ['course', 'requirement', 'is_required', 'is_alternative']
    list_filter = ['course__department', 'requirement__program__department', 'is_required', 'is_alternative']
    search_fields = ['course__title', 'requirement__name']
    ordering = ['requirement__program__department__code', 'requirement__name', 'course__department__code']


@admin.register(ProgramConstraint)
class ProgramConstraintAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'constraint_type', 'is_active']
    list_filter = ['program__department', 'constraint_type', 'is_active']
    search_fields = ['name', 'program__name']
    ordering = ['program__department__code', 'program__name', 'name']
