from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.forms import UserCreationForm
from .models import Course, CourseSchedule, StudentReg
from .forms import LoginForm, RegistrationForm
from .models import Student
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import matplotlib.pyplot as plt
from django.http import HttpRequest
from .models import Course, CourseSchedule, StudentReg,Deadline
from io import BytesIO
import base64
from django.utils import timezone
import json
from django.core.serializers.json import DjangoJSONEncoder


def login_or_register(request):
    global student_id  # Initialize student ID variable globally
    student_id = None  # Initialize student ID variable
    form = None  # Initialize the form variable outside the conditional block
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'login':
            form = LoginForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['username']
                password = form.cleaned_data['password']
                # Query the student table
                student = Student.objects.filter(name=name).first()
                if student and check_password(password, student.password):
                    # Authentication successful
                    student_id = student.student_id  # Save student ID
                    return redirect('course_search')  # Redirect to course search page after successful login
                else:
                    error_message = "Invalid username or password"
                    form = LoginForm()  # Reinitialize form to render it again with error message
        elif action == 'register':
            form = RegistrationForm(request.POST)
            if form.is_valid():
                # Save the user registration data
                email = form.cleaned_data['email']
                name = form.cleaned_data['name']
                password = form.cleaned_data['password']
                hashed_password = make_password(password)
                student = Student(email=email, name=name, password=hashed_password)
                
                # Set the default status for new students regarding prerequisites
                # For example, here we assume new students have no prerequisites completed
                student.has_completed_prerequisites = False
                student.save()
                
                student_id = student.student_id  # Save student ID
                return redirect('login_or_register')  # Redirect to the login page after successful registration
    else:
        form = LoginForm()  # Render login form by default
    return render(request, 'login.html', {'form': form, 'student_id': student_id})



def course_search(request):
    print("Course search view called")  # Debug statement
    query = request.GET.get('q', '')
    print(f"Search query: {query}")  # Debug statement
    action = request.GET.get('action', '')  # Change POST to GET

    courses = Course.objects.all()
    no_courses_message = ""  # Initialize no_courses_message as an empty string

    # Fetch upcoming deadlines
    upcoming_deadlines = Deadline.objects.filter(date__gte=timezone.now())
    upcoming_deadlines_json = json.dumps(list(upcoming_deadlines.values('name', 'date', 'course__name')), cls=DjangoJSONEncoder)

    # Add student-specific logic here if needed
    student_courses = StudentReg.objects.filter(student_id=student_id).values_list('course_id', flat=True)

    if not student_courses:
        # If the student has no registered courses, set the no_courses_message flag
        no_courses_message = "Please add a course."
    else:
        # Filter the courses to only include those registered by the student
        courses = courses.filter(pk__in=student_courses)

    if query:
        # Filter courses by course code, course name, or instructor name
        courses = courses.filter(   
            Q(code__icontains=query) |  # Search by course code
            Q(name__icontains=query) |  # Search by course name
            Q(instructor__icontains=query)  # Search by instructor name
        )

    if action == 'addcourse':
        return redirect('add_course')  # Redirect to the add_course page

    print(f"Found courses: {courses}")  # Debug statement
    return render(request, 'course_search.html', {'courses': courses, 'no_courses_message': no_courses_message, 'upcoming_deadlines_json': upcoming_deadlines_json})





def course_detail(request):
    print("Course search view called")  # Debug statement
    query = request.GET.get('q', '')
    print(f"Search query: {query}")  # Debug statement
    courses = Course.objects.all()

    if query:
        # Filter courses by course code, course name, or instructor name
        courses = courses.filter(   
            Q(code__icontains=query) |  # Search by course code
            Q(name__icontains=query) |  # Search by course name
            Q(instructor__icontains=query)  # Search by instructor name
        )
    return render(request, 'course_detail.html', {'courses': courses})




def add_course(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        try:
            course = Course.objects.get(course_id=course_id)

            # Check if the student has any registered courses
            student_courses = StudentReg.objects.filter(student=student_id)

            # Check if the course has prerequisites
            if course.prerequisites:
                # Check if the student has completed the prerequisites
                completed_prerequisites = StudentReg.objects.filter(student=student_id, course__name=course.prerequisites).exists()
                if not completed_prerequisites:
                    return render(request, 'add_course.html', {
                        'error': f"You need to complete the prerequisite course '{course.prerequisites}' first.",
                        'courses': Course.objects.all()
                    })

            # Handle the case of a new student
            if not student_courses:
                new_student_message = "Welcome! Since you're a new student, you have no registered courses yet."
                # Proceed with course registration for new student

            # Check for availability
            if student_courses.count() >= course.capacity:
                return render(request, 'add_course.html', {
                    'error': "Course is full",
                    'courses': Course.objects.all()
                })

            # Check for schedule clash
            student_schedules = CourseSchedule.objects.filter(course__studentreg__student=student_id)
            if student_schedules.filter(
                Q(days=course.schedule.days) &
                (
                    Q(start_time__lt=course.schedule.end_time, start_time__gte=course.schedule.start_time) |
                    Q(end_time__lte=course.schedule.end_time, end_time__gt=course.schedule.start_time)
                )
            ).exists():
                return render(request, 'add_course.html', {
                    'error': "Schedule clash detected",
                    'courses': Course.objects.all()
                })

            # Register the student for the course
            StudentReg.objects.create(student_id=student_id, course=course)
            return redirect('course_search')

        except Course.DoesNotExist:
            return render(request, 'add_course.html', {
                'error': "Course not found",
                'courses': Course.objects.all()
            })

    return render(request, 'add_course.html', {'courses': Course.objects.all()})





def generate_reports(request):
    # Example report: Course Enrollment
    courses = Course.objects.all()
    course_names = [course.name for course in courses]
    enrollment_counts = [StudentReg.objects.filter(course=course).count() for course in courses]

    # Bar chart for Course Enrollment
    plt.figure(figsize=(10, 5))
    plt.bar(course_names, enrollment_counts)
    plt.xlabel('Courses')
    plt.ylabel('Number of Enrollments')
    plt.title('Course Enrollment Report')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Save bar chart to a string in PNG format
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    enrollment_image_png = buffer.getvalue()
    buffer.close()
    enrollment_image_base64 = base64.b64encode(enrollment_image_png).decode('utf-8')

    # Pie chart for Course Popularity
    plt.figure(figsize=(8, 8))
    plt.pie(enrollment_counts, labels=course_names, autopct='%1.1f%%', startangle=140)
    plt.title('Course Popularity')

    # Save pie chart to a string in PNG format
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    popularity_image_png = buffer.getvalue()
    buffer.close()
    popularity_image_base64 = base64.b64encode(popularity_image_png).decode('utf-8')

    return render(request, 'generate_reports.html', {
        'enrollment_image_base64': enrollment_image_base64,
        'popularity_image_base64': popularity_image_base64,
    })











