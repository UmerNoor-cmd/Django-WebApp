# Generated by Django 5.0.6 on 2024-05-17 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_alter_student_options_alter_student_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
