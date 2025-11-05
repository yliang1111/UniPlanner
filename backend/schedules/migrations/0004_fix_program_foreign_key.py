# Generated manually to fix program foreign key constraint

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedules', '0003_rename_degree_program_to_program'),
        ('courses', '0008_alter_program_department'),
    ]

    operations = [
        migrations.AlterField(
            model_name='degreeaudit',
            name='program',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='audits',
                to='courses.program'
            ),
        ),
    ]

