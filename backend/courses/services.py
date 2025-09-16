from collections import defaultdict, deque
from typing import List, Set, Dict, Tuple
from django.db.models import Q
from .models import Course, Prerequisite


class PrerequisiteValidator:
    """
    Service class for validating course prerequisites using graph traversal algorithms.
    Implements topological sorting and cycle detection for prerequisite chains.
    """
    
    def __init__(self, student_profile):
        self.student = student_profile
        from users.models import CompletedCourse
        self.completed_courses = set(
            student_profile.completed_courses
            .filter(grade__in=['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'P'])
            .values_list('course_id', flat=True)
        )
    
    def can_take_course(self, course: Course) -> Tuple[bool, List[str]]:
        """
        Check if a student can take a specific course based on prerequisites.
        
        Returns:
            Tuple of (can_take: bool, missing_prerequisites: List[str])
        """
        missing_prerequisites = []
        
        # Get all prerequisites for this course
        prerequisites = course.prerequisites.all()
        
        for prereq in prerequisites:
            if prereq.prerequisite_course.id not in self.completed_courses:
                missing_prerequisites.append(prereq.prerequisite_course.full_code)
        
        can_take = len(missing_prerequisites) == 0
        return can_take, missing_prerequisites
    
    def get_available_courses(self, courses: List[Course] = None) -> List[Course]:
        """
        Get all courses that a student can take (prerequisites satisfied).
        
        Args:
            courses: Optional list of courses to check. If None, checks all active courses.
        
        Returns:
            List of courses the student can take
        """
        if courses is None:
            courses = Course.objects.filter(is_active=True)
        
        available_courses = []
        for course in courses:
            can_take, _ = self.can_take_course(course)
            if can_take:
                available_courses.append(course)
        
        return available_courses
    
    def get_prerequisite_chain(self, course: Course) -> Dict[str, List[str]]:
        """
        Get the complete prerequisite chain for a course using BFS.
        
        Returns:
            Dictionary with course codes as keys and their prerequisites as values
        """
        chain = defaultdict(list)
        visited = set()
        queue = deque([course])
        
        while queue:
            current_course = queue.popleft()
            
            if current_course.id in visited:
                continue
            
            visited.add(current_course.id)
            prerequisites = current_course.prerequisites.all()
            
            for prereq in prerequisites:
                prereq_course = prereq.prerequisite_course
                chain[current_course.full_code].append(prereq_course.full_code)
                
                if prereq_course.id not in visited:
                    queue.append(prereq_course)
        
        return dict(chain)
    
    def detect_prerequisite_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the prerequisite graph using DFS.
        
        Returns:
            List of cycles found in the prerequisite graph
        """
        all_courses = Course.objects.filter(is_active=True)
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(course, path):
            if course.id in rec_stack:
                # Found a cycle
                cycle_start = path.index(course.full_code)
                cycle = path[cycle_start:] + [course.full_code]
                cycles.append(cycle)
                return
            
            if course.id in visited:
                return
            
            visited.add(course.id)
            rec_stack.add(course.id)
            path.append(course.full_code)
            
            # Visit all prerequisites
            for prereq in course.prerequisites.all():
                dfs(prereq.prerequisite_course, path.copy())
            
            rec_stack.remove(course.id)
        
        for course in all_courses:
            if course.id not in visited:
                dfs(course, [])
        
        return cycles
    
    def get_topological_order(self) -> List[str]:
        """
        Get courses in topological order (prerequisites first) using Kahn's algorithm.
        
        Returns:
            List of course codes in topological order
        """
        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        all_courses = Course.objects.filter(is_active=True)
        course_map = {course.id: course for course in all_courses}
        
        for course in all_courses:
            in_degree[course.full_code] = 0
        
        for course in all_courses:
            for prereq in course.prerequisites.all():
                graph[prereq.prerequisite_course.full_code].append(course.full_code)
                in_degree[course.full_code] += 1
        
        # Kahn's algorithm
        queue = deque([course for course, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            current = queue.popleft()
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result
    
    def get_recommended_course_sequence(self, target_course: Course = None) -> List[Dict]:
        """
        Get a recommended sequence of courses for a student.
        
        Args:
            target_course: Optional target course to work towards
        
        Returns:
            List of course recommendations with metadata
        """
        if target_course:
            # Get path to target course
            return self._get_path_to_course(target_course)
        else:
            # Get general recommendations based on completed courses
            return self._get_general_recommendations()
    
    def _get_path_to_course(self, target_course: Course) -> List[Dict]:
        """Get the optimal path to a target course"""
        # Use BFS to find shortest path
        queue = deque([(target_course, [])])
        visited = set()
        
        while queue:
            course, path = queue.popleft()
            
            if course.id in visited:
                continue
            
            visited.add(course.id)
            
            # Check if student can take this course
            can_take, missing = self.can_take_course(course)
            
            if can_take:
                return [{
                    'course': course,
                    'can_take': True,
                    'missing_prerequisites': [],
                    'credits': course.credits,
                    'path_position': len(path)
                }] + path
            
            # Add prerequisites to queue
            for prereq in course.prerequisites.all():
                if prereq.prerequisite_course.id not in visited:
                    new_path = [{
                        'course': course,
                        'can_take': can_take,
                        'missing_prerequisites': missing,
                        'credits': course.credits,
                        'path_position': len(path)
                    }] + path
                    queue.append((prereq.prerequisite_course, new_path))
        
        return []
    
    def _get_general_recommendations(self) -> List[Dict]:
        """Get general course recommendations"""
        available_courses = self.get_available_courses()
        
        recommendations = []
        for course in available_courses:
            # Calculate priority based on various factors
            priority = self._calculate_course_priority(course)
            
            recommendations.append({
                'course': course,
                'can_take': True,
                'missing_prerequisites': [],
                'credits': course.credits,
                'priority': priority,
                'reason': self._get_recommendation_reason(course)
            })
        
        # Sort by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        return recommendations[:10]  # Return top 10 recommendations
    
    def _calculate_course_priority(self, course: Course) -> float:
        """Calculate priority score for a course"""
        score = 0.0
        
        # Base score from credits
        score += course.credits * 0.1
        
        # Bonus for courses that unlock many other courses
        unlocks_count = Prerequisite.objects.filter(prerequisite_course=course).count()
        score += unlocks_count * 0.5
        
        # Bonus for courses in student's degree program
        if hasattr(self.student, 'degrees'):
            for degree in self.student.degrees.all():
                if course.degree_requirements.filter(requirement__degree_program=degree.degree_program).exists():
                    score += 1.0
        
        return score
    
    def _get_recommendation_reason(self, course: Course) -> str:
        """Get human-readable reason for recommending a course"""
        unlocks_count = Prerequisite.objects.filter(prerequisite_course=course).count()
        
        if unlocks_count > 3:
            return f"Unlocks {unlocks_count} other courses"
        elif course.credits >= 4:
            return "High credit course"
        else:
            return "Available prerequisite"
