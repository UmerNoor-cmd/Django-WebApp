from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import Course, CourseSchedule, StudentReg

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('course_search')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def course_search(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        courses = Course.objects.filter(course_name__icontains=query) if query else Course.objects.all()
        return render(request, 'course_search.html', {'courses': courses})

def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    schedules = CourseSchedule.objects.filter(course=course)
    return render(request, 'course_detail.html', {'course': course, 'schedules': schedules})

def add_course(request, course_id):
    course = Course.objects.get(id=course_id)
    student = request.user
    if StudentReg.objects.filter(student=student, course=course).exists():
        # Already registered
        pass
    else:
        prereqs_met = all(prereq in student.courses.all() for prereq in course.prerequisites.all())
        if prereqs_met:
            StudentReg.objects.create(student=student, course=course)
    return redirect('view_schedule')

def view_schedule(request):
    student = request.user
    registrations = StudentReg.objects.filter(student=student)
    return render(request, 'view_schedule.html', {'registrations': registrations})
