# Generated by Django 4.0.1 on 2022-07-03 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_facultyname'),
    ]

    operations = [
        migrations.RenameField(
            model_name='universities',
            old_name='gov_id',
            new_name='gov',
        ),
    ]
