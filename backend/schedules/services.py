from typing import List, Dict, Tuple, Set
from datetime import time, datetime
from django.db.models import Q
from .models import Schedule, ScheduleItem
from courses.models import CourseOffering, TimeSlot


class ScheduleConflictDetector:
    """
    Service class for detecting and resolving schedule conflicts.
    Implements advanced conflict detection algorithms for course scheduling.
    """
    
    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.time_slots = self._get_schedule_time_slots()
    
    def _get_schedule_time_slots(self) -> List[Dict]:
        """Get all time slots for courses in the schedule"""
        time_slots = []
        
        for item in self.schedule.schedule_items.all():
            for time_slot in item.offering.time_slots.all():
                time_slots.append({
                    'id': time_slot.id,
                    'day': time_slot.day_of_week,
                    'start': time_slot.start_time,
                    'end': time_slot.end_time,
                    'course': item.offering.course.full_code,
                    'offering': item.offering,
                    'location': time_slot.location
                })
        
        return time_slots
    
    def detect_conflicts(self) -> List[Dict]:
        """
        Detect all conflicts in the schedule.
        
        Returns:
            List of conflict objects with details
        """
        conflicts = []
        time_slots = self.time_slots
        
        # Check for time conflicts
        for i, slot1 in enumerate(time_slots):
            for j, slot2 in enumerate(time_slots[i+1:], i+1):
                if self._times_overlap(slot1, slot2):
                    conflicts.append({
                        'type': 'time_conflict',
                        'severity': 'high',
                        'description': f"Time conflict between {slot1['course']} and {slot2['course']}",
                        'courses': [slot1['course'], slot2['course']],
                        'day': slot1['day'],
                        'time_range': self._get_overlap_time_range(slot1, slot2),
                        'locations': [slot1['location'], slot2['location']]
                    })
        
        # Check for location conflicts
        location_conflicts = self._detect_location_conflicts()
        conflicts.extend(location_conflicts)
        
        # Check for instructor conflicts
        instructor_conflicts = self._detect_instructor_conflicts()
        conflicts.extend(instructor_conflicts)
        
        return conflicts
    
    def _times_overlap(self, slot1: Dict, slot2: Dict) -> bool:
        """Check if two time slots overlap"""
        if slot1['day'] != slot2['day']:
            return False
        
        start1, end1 = slot1['start'], slot1['end']
        start2, end2 = slot2['start'], slot2['end']
        
        # Two time ranges overlap if one starts before the other ends
        return not (end1 <= start2 or end2 <= start1)
    
    def _get_overlap_time_range(self, slot1: Dict, slot2: Dict) -> Tuple[time, time]:
        """Get the time range where two slots overlap"""
        start1, end1 = slot1['start'], slot1['end']
        start2, end2 = slot2['start'], slot2['end']
        
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        return overlap_start, overlap_end
    
    def _detect_location_conflicts(self) -> List[Dict]:
        """Detect conflicts where multiple courses use the same location at the same time"""
        conflicts = []
        location_schedule = {}
        
        for slot in self.time_slots:
            if not slot['location']:
                continue
            
            key = (slot['day'], slot['start'], slot['end'], slot['location'])
            
            if key in location_schedule:
                conflicts.append({
                    'type': 'location_conflict',
                    'severity': 'high',
                    'description': f"Location conflict: {slot['course']} and {location_schedule[key]['course']} both scheduled in {slot['location']}",
                    'courses': [slot['course'], location_schedule[key]['course']],
                    'day': slot['day'],
                    'time_range': (slot['start'], slot['end']),
                    'location': slot['location']
                })
            else:
                location_schedule[key] = slot
        
        return conflicts
    
    def _detect_instructor_conflicts(self) -> List[Dict]:
        """Detect conflicts where an instructor is scheduled to teach multiple courses simultaneously"""
        conflicts = []
        instructor_schedule = {}
        
        for slot in self.time_slots:
            offering = slot['offering']
            if not offering.instructor:
                continue
            
            key = (slot['day'], slot['start'], slot['end'], offering.instructor)
            
            if key in instructor_schedule:
                conflicts.append({
                    'type': 'instructor_conflict',
                    'severity': 'high',
                    'description': f"Instructor conflict: {offering.instructor} scheduled for both {slot['course']} and {instructor_schedule[key]['course']}",
                    'courses': [slot['course'], instructor_schedule[key]['course']],
                    'day': slot['day'],
                    'time_range': (slot['start'], slot['end']),
                    'instructor': offering.instructor
                })
            else:
                instructor_schedule[key] = slot
        
        return conflicts
    
    def can_add_course(self, offering: CourseOffering) -> Tuple[bool, List[Dict]]:
        """
        Check if a course offering can be added to the schedule without conflicts.
        
        Args:
            offering: The course offering to check
        
        Returns:
            Tuple of (can_add: bool, conflicts: List[Dict])
        """
        # Get time slots for the new offering
        new_slots = []
        for time_slot in offering.time_slots.all():
            new_slots.append({
                'day': time_slot.day_of_week,
                'start': time_slot.start_time,
                'end': time_slot.end_time,
                'course': offering.course.full_code,
                'offering': offering,
                'location': time_slot.location
            })
        
        # Check for conflicts with existing schedule
        conflicts = []
        for new_slot in new_slots:
            for existing_slot in self.time_slots:
                if self._times_overlap(new_slot, existing_slot):
                    conflicts.append({
                        'type': 'time_conflict',
                        'severity': 'high',
                        'description': f"Would conflict with {existing_slot['course']}",
                        'courses': [new_slot['course'], existing_slot['course']],
                        'day': new_slot['day'],
                        'time_range': self._get_overlap_time_range(new_slot, existing_slot)
                    })
        
        can_add = len(conflicts) == 0
        return can_add, conflicts
    
    def suggest_alternatives(self, conflicting_offering: CourseOffering) -> List[CourseOffering]:
        """
        Suggest alternative offerings for a course that conflicts with the schedule.
        
        Args:
            conflicting_offering: The offering that conflicts
        
        Returns:
            List of alternative offerings that don't conflict
        """
        alternatives = []
        course = conflicting_offering.course
        
        # Get all other offerings for the same course
        other_offerings = CourseOffering.objects.filter(
            course=course,
            semester=self.schedule.semester,
            year=self.schedule.year
        ).exclude(id=conflicting_offering.id)
        
        for offering in other_offerings:
            can_add, _ = self.can_add_course(offering)
            if can_add:
                alternatives.append(offering)
        
        return alternatives
    
    def optimize_schedule(self) -> Dict:
        """
        Suggest optimizations for the current schedule.
        
        Returns:
            Dictionary with optimization suggestions
        """
        suggestions = {
            'conflicts': self.detect_conflicts(),
            'gaps': self._find_schedule_gaps(),
            'workload': self._analyze_workload(),
            'recommendations': []
        }
        
        # Generate recommendations
        if suggestions['conflicts']:
            suggestions['recommendations'].append({
                'type': 'resolve_conflicts',
                'priority': 'high',
                'message': f"Resolve {len(suggestions['conflicts'])} conflicts in your schedule"
            })
        
        if suggestions['gaps']:
            suggestions['recommendations'].append({
                'type': 'fill_gaps',
                'priority': 'medium',
                'message': f"Consider filling {len(suggestions['gaps'])} time gaps in your schedule"
            })
        
        return suggestions
    
    def _find_schedule_gaps(self) -> List[Dict]:
        """Find gaps in the schedule that could be filled"""
        gaps = []
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        for day in days:
            day_slots = [slot for slot in self.time_slots if slot['day'] == day]
            day_slots.sort(key=lambda x: x['start'])
            
            # Find gaps between classes
            for i in range(len(day_slots) - 1):
                current_end = day_slots[i]['end']
                next_start = day_slots[i + 1]['start']
                
                # Gap of at least 1 hour
                if self._time_difference(current_end, next_start) >= 60:
                    gaps.append({
                        'day': day,
                        'start': current_end,
                        'end': next_start,
                        'duration_minutes': self._time_difference(current_end, next_start)
                    })
        
        return gaps
    
    def _analyze_workload(self) -> Dict:
        """Analyze the workload distribution across days"""
        daily_credits = {}
        daily_hours = {}
        
        for slot in self.time_slots:
            day = slot['day']
            course = slot['offering'].course
            
            if day not in daily_credits:
                daily_credits[day] = 0
                daily_hours[day] = 0
            
            daily_credits[day] += course.credits
            daily_hours[day] += self._time_difference(slot['start'], slot['end'])
        
        return {
            'daily_credits': daily_credits,
            'daily_hours': daily_hours,
            'total_credits': sum(daily_credits.values()),
            'total_hours': sum(daily_hours.values())
        }
    
    def _time_difference(self, start: time, end: time) -> int:
        """Calculate time difference in minutes"""
        start_minutes = start.hour * 60 + start.minute
        end_minutes = end.hour * 60 + end.minute
        return end_minutes - start_minutes
