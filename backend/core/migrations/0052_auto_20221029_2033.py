# Generated by Django 3.2.16 on 2022-10-29 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0051_auto_20221026_2357'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fulfillment',
            old_name='code',
            new_name='typeid',
        ),
        migrations.AddField(
            model_name='fulfillment',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
