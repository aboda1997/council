# Generated by Django 3.2.13 on 2022-07-24 09:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_studentssecondaryedu_student_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Months',
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
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'months',
            },
        ),
        migrations.RemoveField(
            model_name='students',
            name='studentFulfillment',
        ),
        migrations.AddField(
            model_name='studentssecondaryedu',
            name='studentFulfillment',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='student_fulfillment',
                to='core.fulfillment',
            ),
        ),
        migrations.AlterField(
            model_name='studentsuniversityedu',
            name='studentExpectedGraduationYear',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='student_expected_graduation_year',
                to='core.years',
            ),
        ),
        migrations.AlterField(
            model_name='studentsuniversityedu',
            name='studentExpectedGraduationMonth',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='student_expected_graduation_month',
                to='core.months',
            ),
        ),
    ]
