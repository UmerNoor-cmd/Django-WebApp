from django.db import models

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name



class CourseSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    days = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_no = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.days} {self.start_time}-{self.end_time}"



class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    instructor = models.CharField(max_length=100)
    prerequisites = models.CharField(max_length=255, blank=True, default='')
    capacity = models.IntegerField()
    schedule= models.ForeignKey(CourseSchedule, on_delete=models.CASCADE)


    class Meta:
        unique_together = [('schedule',)]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Deadline(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.course.code})"

class StudentReg(models.Model):
    reg_id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')
