# Generated by Django 4.0.1 on 2022-07-20 12:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_studentsuniversityedu'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentsImposedCourses',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('createdBy', models.IntegerField(blank=True, default=0)),
                ('updatedAt', models.DateTimeField(null=True)),
                ('updatedBy', models.IntegerField(null=True)),
                (
                    'imposedCourse',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_imposed_course',
                        to='core.imposedcourses',
                    ),
                ),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='core.students'
                    ),
                ),
            ],
            options={
                'db_table': 'studentsimposedcourses',
            },
        ),
    ]
