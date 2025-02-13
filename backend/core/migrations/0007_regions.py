# Generated by Django 4.0.1 on 2022-07-03 11:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_controllist_educationaladministrations_governorates_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Regions',
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
                ('type', models.CharField(blank=True, max_length=11, null=True)),
                ('typeid', models.CharField(max_length=100)),
                ('parent', models.CharField(blank=True, max_length=11, null=True)),
                ('gscdid', models.CharField(blank=True, max_length=11, null=True)),
                ('latitude', models.CharField(blank=True, max_length=100, null=True)),
                ('longitude', models.CharField(blank=True, max_length=100, null=True)),
                ('tansiqid', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'regions',
            },
        ),
    ]
