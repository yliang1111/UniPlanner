from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from users.models import UserProfile, StudentProfile


class Command(BaseCommand):
    help = 'Create default admin and guest users'

    def handle(self, *args, **options):
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS('Admin user created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )

        # Create guest user
        guest_user, created = User.objects.get_or_create(
            username='guest',
            defaults={
                'is_staff': False,
                'is_superuser': False,
                'is_active': True
            }
        )
        if created:
            guest_user.set_password('guest123')
            guest_user.save()
            self.stdout.write(
                self.style.SUCCESS('Guest user created successfully')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Guest user already exists')
            )

        # Create profiles for both users
        for user in [admin_user, guest_user]:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'admin' if user.username == 'admin' else 'student',
                    'phone': '',
                    'address': '',
                    'date_of_birth': None
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Profile created for {user.username}')
                )

        # Create student profile for guest user
        if guest_user:
            student_profile, created = StudentProfile.objects.get_or_create(
                user=guest_user,
                defaults={
                    'student_id': 'GUEST001',
                    'graduation_year': None,
                    'gpa': None,
                    'enrollment_status': 'active'
                }
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS('Student profile created for guest user')
                )

        self.stdout.write(
            self.style.SUCCESS('Default users setup completed')
        )


