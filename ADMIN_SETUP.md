# Admin and Guest User Setup

## Fixed Admin Account

The UniPlanner application comes with a pre-configured admin account that cannot be changed:

- **Username**: `admin`
- **Password**: `admin123`

## Guest Account

The application also includes a guest account for users who want to explore the system without creating an account:

- **Username**: `guest`
- **Password**: `guest123`

## Security Features

### 1. Password Protection
- The admin password is automatically reset to `admin123` on every server restart
- The guest password is automatically reset to `guest123` on every server restart
- The passwords cannot be permanently changed through the application
- A Django management command ensures the passwords are always reset

### 2. Automatic Setup
- The admin and guest users are created automatically during database migrations
- The admin profile is set up with the correct role and permissions
- The guest profile is set up as a student with limited access
- No manual setup is required

### 3. Management Commands

#### Create/Update Admin and Guest Users
```bash
python manage.py create_admin
```
This command:
- Creates the admin user if it doesn't exist
- Creates the guest user if it doesn't exist
- Resets the admin password to `admin123`
- Resets the guest password to `guest123`
- Sets up the admin profile with the correct role
- Sets up the guest profile as a student
- Removes any student profile from admin (admin shouldn't have one)

## Admin Capabilities

The admin user has access to:

1. **Course Management**
   - Create, edit, and delete courses
   - Manage course prerequisites, corequisites, and antirequisites
   - Set course restrictions by major
   - Update course descriptions, credits, and other details

2. **System Administration**
   - Full Django admin panel access
   - User management capabilities
   - Database administration

3. **API Access**
   - All admin API endpoints
   - Course management APIs
   - User management APIs

## Guest User Capabilities

The guest user has access to:

1. **Student Features**
   - View course catalog
   - Build schedules
   - View degree audit
   - Access student dashboard

2. **Restrictions**
   - Cannot access admin functions
   - Cannot modify course data
   - Cannot access admin panel
   - Guest indicator shown in UI

## Technical Implementation

### Database Migration
- Migration `0003_auto_20250916_0612.py` creates the admin and guest users automatically
- Runs during `python manage.py migrate`

### Signals
- `post_migrate` signal ensures admin and guest users exist after migrations
- `user_logged_in` signal resets passwords on every login

### Middleware
- Password reset middleware prevents permanent password changes
- Ensures admin and guest credentials remain fixed

## Usage

1. **Admin Login**: Use `admin` / `admin123` to log in as administrator
2. **Guest Login**: Use `guest` / `guest123` to log in as guest user
3. **Access Admin Panel**: Navigate to `/admin/courses` for course management (admin only)
4. **Reset Passwords**: Run `python manage.py create_admin` if needed

## Security Notes

- The admin and guest accounts are designed for development and testing
- In production, consider additional security measures
- The fixed passwords ensure consistent access for development
- Admin privileges are clearly separated from regular user accounts
- Guest users have limited access and cannot modify system data

## Troubleshooting

If you cannot log in with admin or guest credentials:

1. Run the management command:
   ```bash
   python manage.py create_admin
   ```

2. Check the database:
   ```bash
   python manage.py shell -c "from django.contrib.auth.models import User; print('Admin:', User.objects.get(username='admin').check_password('admin123')); print('Guest:', User.objects.get(username='guest').check_password('guest123'))"
   ```

3. Verify the profiles:
   ```bash
   python manage.py shell -c "from users.models import UserProfile; print('Admin role:', UserProfile.objects.get(user__username='admin').role); print('Guest role:', UserProfile.objects.get(user__username='guest').role)"
   ```
