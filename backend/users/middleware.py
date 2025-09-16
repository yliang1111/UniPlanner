from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def reset_admin_password(sender, request, user, **kwargs):
    """Reset admin and guest passwords on every login to prevent changes"""
    if user.username == 'admin':
        # Always reset the password to admin123
        user.set_password('admin123')
        user.save()
    elif user.username == 'guest':
        # Always reset the password to guest123
        user.set_password('guest123')
        user.save()
