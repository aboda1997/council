# Generated by Django 4.0.1 on 2022-07-20 12:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_students'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentsSecondaryEdu',
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
                ('studentSchool', models.CharField(max_length=200, null=True)),
                ('studentDept', models.CharField(max_length=200, null=True)),
                ('studentSeatNumber', models.CharField(max_length=20, null=True)),
                ('studentTot', models.CharField(max_length=10, null=True)),
                ('studentEquivTot', models.CharField(max_length=10, null=True)),
                ('studentSportDegree', models.CharField(max_length=10, null=True)),
                ('studentComplainGain', models.CharField(max_length=10, null=True)),
                (
                    'student',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='core.students'
                    ),
                ),
                (
                    'studentCertificateYear',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='certificate_year',
                        to='core.years',
                    ),
                ),
                (
                    'studentDeptCode',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_dept',
                        to='core.regions',
                    ),
                ),
                (
                    'studentGov',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_gov',
                        to='core.regions',
                    ),
                ),
                (
                    'studentSchoolType',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_school',
                        to='core.schooltype',
                    ),
                ),
                (
                    'studentSecondaryCert',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_cert',
                        to='core.certificates',
                    ),
                ),
                (
                    'studentStudyGroup',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='student_group',
                        to='core.studygroups',
                    ),
                ),
            ],
            options={
                'db_table': 'studentssecondaryedu',
            },
        ),
    ]
