from django.db import models
from django.contrib.auth.models import AbstractUser

class Student(AbstractUser):
    # Extending the default User model
    email = models.EmailField(unique=True)

class Course(models.Model):
    course_code = models.CharField(max_length=10, unique=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField()
    instructor_name = models.CharField(max_length=100)
    prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False)
    capacity = models.IntegerField()

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    days = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_no = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.course.course_code} - {self.days} {self.start_time}-{self.end_time}"

class StudentReg(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')
