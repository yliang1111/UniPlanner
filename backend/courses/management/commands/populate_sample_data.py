from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import (
    Department, Course, Prerequisite, DegreeProgram, DegreeRequirement,
    CourseRequirement, CourseOffering, TimeSlot
)
from users.models import StudentProfile, StudentDegree, CompletedCourse
from schedules.models import Schedule, ScheduleItem, DegreeAudit
from datetime import time, date


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Create departments
        cs_dept = Department.objects.create(
            code='CS',
            name='Computer Science'
        )
        math_dept = Department.objects.create(
            code='MATH',
            name='Mathematics'
        )
        eng_dept = Department.objects.create(
            code='ENG',
            name='English'
        )

        # Create courses
        cs101 = Course.objects.create(
            department=cs_dept,
            course_number='101',
            title='Introduction to Computer Science',
            description='Basic concepts of computer science and programming',
            credits=3
        )

        cs201 = Course.objects.create(
            department=cs_dept,
            course_number='201',
            title='Data Structures',
            description='Fundamental data structures and algorithms',
            credits=4
        )

        cs301 = Course.objects.create(
            department=cs_dept,
            course_number='301',
            title='Algorithms',
            description='Advanced algorithms and complexity analysis',
            credits=4
        )

        cs401 = Course.objects.create(
            department=cs_dept,
            course_number='401',
            title='Software Engineering',
            description='Software development methodologies and practices',
            credits=3
        )

        math101 = Course.objects.create(
            department=math_dept,
            course_number='101',
            title='Calculus I',
            description='Differential and integral calculus',
            credits=4
        )

        math201 = Course.objects.create(
            department=math_dept,
            course_number='201',
            title='Calculus II',
            description='Advanced calculus topics',
            credits=4
        )

        eng101 = Course.objects.create(
            department=eng_dept,
            course_number='101',
            title='Composition',
            description='Basic writing and composition skills',
            credits=3
        )

        # Create prerequisites
        Prerequisite.objects.create(course=cs201, prerequisite_course=cs101)
        Prerequisite.objects.create(course=cs301, prerequisite_course=cs201)
        Prerequisite.objects.create(course=cs401, prerequisite_course=cs301)
        Prerequisite.objects.create(course=math201, prerequisite_course=math101)

        # Create degree program
        cs_degree = DegreeProgram.objects.create(
            name='Bachelor of Science in Computer Science',
            department=cs_dept,
            total_credits_required=120,
            description='Comprehensive computer science degree program'
        )

        # Create degree requirements
        core_requirement = DegreeRequirement.objects.create(
            degree_program=cs_degree,
            requirement_type='core',
            name='Core Computer Science Courses',
            description='Required computer science courses',
            credits_required=30
        )

        math_requirement = DegreeRequirement.objects.create(
            degree_program=cs_degree,
            requirement_type='general_ed',
            name='Mathematics Requirements',
            description='Required mathematics courses',
            credits_required=8
        )

        eng_requirement = DegreeRequirement.objects.create(
            degree_program=cs_degree,
            requirement_type='general_ed',
            name='English Requirements',
            description='Required English courses',
            credits_required=3
        )

        # Create course requirements
        CourseRequirement.objects.create(
            requirement=core_requirement,
            course=cs101,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=core_requirement,
            course=cs201,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=core_requirement,
            course=cs301,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=core_requirement,
            course=cs401,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=math_requirement,
            course=math101,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=math_requirement,
            course=math201,
            is_required=True
        )
        CourseRequirement.objects.create(
            requirement=eng_requirement,
            course=eng101,
            is_required=True
        )

        # Create course offerings for current semester
        current_year = 2024
        current_semester = 'fall'

        cs101_offering = CourseOffering.objects.create(
            course=cs101,
            semester=current_semester,
            year=current_year,
            section='001',
            instructor='Dr. Smith',
            capacity=30,
            enrolled=25
        )

        cs201_offering = CourseOffering.objects.create(
            course=cs201,
            semester=current_semester,
            year=current_year,
            section='001',
            instructor='Dr. Johnson',
            capacity=25,
            enrolled=20
        )

        math101_offering = CourseOffering.objects.create(
            course=math101,
            semester=current_semester,
            year=current_year,
            section='001',
            instructor='Dr. Brown',
            capacity=35,
            enrolled=30
        )

        eng101_offering = CourseOffering.objects.create(
            course=eng101,
            semester=current_semester,
            year=current_year,
            section='001',
            instructor='Dr. Davis',
            capacity=25,
            enrolled=22
        )

        # Create time slots
        TimeSlot.objects.create(
            offering=cs101_offering,
            day_of_week='monday',
            start_time=time(9, 0),
            end_time=time(10, 30),
            location='CS Building 101'
        )
        TimeSlot.objects.create(
            offering=cs101_offering,
            day_of_week='wednesday',
            start_time=time(9, 0),
            end_time=time(10, 30),
            location='CS Building 101'
        )

        TimeSlot.objects.create(
            offering=cs201_offering,
            day_of_week='tuesday',
            start_time=time(11, 0),
            end_time=time(12, 30),
            location='CS Building 201'
        )
        TimeSlot.objects.create(
            offering=cs201_offering,
            day_of_week='thursday',
            start_time=time(11, 0),
            end_time=time(12, 30),
            location='CS Building 201'
        )

        TimeSlot.objects.create(
            offering=math101_offering,
            day_of_week='monday',
            start_time=time(10, 0),
            end_time=time(11, 0),
            location='Math Building 101'
        )
        TimeSlot.objects.create(
            offering=math101_offering,
            day_of_week='wednesday',
            start_time=time(10, 0),
            end_time=time(11, 0),
            location='Math Building 101'
        )
        TimeSlot.objects.create(
            offering=math101_offering,
            day_of_week='friday',
            start_time=time(10, 0),
            end_time=time(11, 0),
            location='Math Building 101'
        )

        TimeSlot.objects.create(
            offering=eng101_offering,
            day_of_week='tuesday',
            start_time=time(14, 0),
            end_time=time(15, 30),
            location='English Building 101'
        )
        TimeSlot.objects.create(
            offering=eng101_offering,
            day_of_week='thursday',
            start_time=time(14, 0),
            end_time=time(15, 30),
            location='English Building 101'
        )

        # Create student profile for admin user
        admin_user = User.objects.get(username='admin')
        student_profile = StudentProfile.objects.create(
            user=admin_user,
            student_id='STU001',
            graduation_year=2025,
            gpa=3.5,
            total_credits_earned=60
        )

        # Create student degree
        StudentDegree.objects.create(
            student=student_profile,
            degree_program=cs_degree,
            start_date=date(2021, 9, 1),
            expected_graduation=date(2025, 5, 15),
            is_primary=True
        )

        # Create completed courses
        CompletedCourse.objects.create(
            student=student_profile,
            course=cs101,
            semester='fall',
            year=2021,
            grade='A',
            credits_earned=3
        )

        CompletedCourse.objects.create(
            student=student_profile,
            course=math101,
            semester='fall',
            year=2021,
            grade='B+',
            credits_earned=4
        )

        CompletedCourse.objects.create(
            student=student_profile,
            course=eng101,
            semester='spring',
            year=2022,
            grade='A-',
            credits_earned=3
        )

        # Create a sample schedule
        schedule = Schedule.objects.create(
            student=student_profile,
            semester=current_semester,
            year=current_year,
            name='Fall 2024 Schedule',
            is_active=True
        )

        # Add courses to schedule
        ScheduleItem.objects.create(
            schedule=schedule,
            offering=cs201_offering
        )

        ScheduleItem.objects.create(
            schedule=schedule,
            offering=math101_offering
        )

        # Create degree audit
        DegreeAudit.objects.create(
            student=student_profile,
            degree_program=cs_degree
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

