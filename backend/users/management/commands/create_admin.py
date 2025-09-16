from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, StudentProfile


class Command(BaseCommand):
    help = 'Create or update the fixed admin user'

    def handle(self, *args, **options):
        # Create or get the admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@uniplanner.edu',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        # Always set the password to admin123 (in case it was changed)
        admin_user.set_password('admin123')
        admin_user.save()
        
        # Create or get the admin profile
        admin_profile, profile_created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': 'admin',
                'phone': '',
                'address': 'System Administrator',
            }
        )
        
        # Ensure the profile is set to admin role
        if admin_profile.role != 'admin':
            admin_profile.role = 'admin'
            admin_profile.save()
        
        # Remove any student profile if it exists (admin shouldn't have one)
        try:
            student_profile = admin_user.student_profile
            student_profile.delete()
            self.stdout.write(
                self.style.WARNING('Removed student profile from admin user')
            )
        except StudentProfile.DoesNotExist:
            pass
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created admin user')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Successfully updated admin user')
            )
        
        # Create or get the guest user
        guest_user, guest_created = User.objects.get_or_create(
            username='guest',
            defaults={
                'email': 'guest@uniplanner.edu',
                'first_name': 'Guest',
                'last_name': 'User',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        
        # Always set the password to guest123 (in case it was changed)
        guest_user.set_password('guest123')
        guest_user.save()
        
        # Create or get the guest profile
        guest_profile, guest_profile_created = UserProfile.objects.get_or_create(
            user=guest_user,
            defaults={
                'role': 'student',
                'phone': '',
                'address': 'Guest User',
            }
        )
        
        # Ensure the profile is set to student role
        if guest_profile.role != 'student':
            guest_profile.role = 'student'
            guest_profile.save()
        
        # Create or get the guest student profile
        guest_student_profile, guest_student_created = StudentProfile.objects.get_or_create(
            user=guest_user,
            defaults={
                'student_id': 'GUEST001',
                'graduation_year': 2025,
                'gpa': 3.5,
                'total_credits_earned': 0,
                'enrollment_status': 'active',
            }
        )
        
        if guest_created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created guest user')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Successfully updated guest user')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Admin credentials: username=admin, password=admin123')
        )
        self.stdout.write(
            self.style.SUCCESS('Guest credentials: username=guest, password=guest123')
        )
