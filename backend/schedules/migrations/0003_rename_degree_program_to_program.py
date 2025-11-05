# Generated manually to rename degree_program to program

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0002_alter_degreeaudit_options'),
        ('courses', '0008_alter_program_department'),
    ]

    operations = [
        migrations.RenameField(
            model_name='degreeaudit',
            old_name='degree_program',
            new_name='program',
        ),
        migrations.AlterUniqueTogether(
            name='degreeaudit',
            unique_together={('student', 'program')},
        ),
    ]

