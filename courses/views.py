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

def login_or_register(request):
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
                student.save()
                return redirect('login_or_register')  # Redirect to the login page after successful registration
    else:
        form = LoginForm()  # Render login form by default
    return render(request, 'login.html', {'form': form})


def course_search(request):
    print("Course search view called")  # Debug statement
    query = request.GET.get('q', '')
    print(f"Search query: {query}")  # Debug statement
    action = request.POST.get('action')

    courses = Course.objects.all()

    if query:
        # Filter courses by course code, course name, or instructor name
        courses = courses.filter(
            Q(code__icontains=query) |  # Search by course code
            Q(name__icontains=query) |  # Search by course name
            Q(instructor__icontains=query)  # Search by instructor name
        )

    elif action == 'addcourse':

        return redirect('add_course')  # Redirect to the login page after successful registration
    print(f"Found courses: {courses}")  # Debug statement
    return render(request, 'course_search.html', {'courses': courses})


def register_courses(request):
    if request.method == 'POST':
        selected_course_ids = request.POST.getlist('courses')  # Get the list of selected course IDs from the form data
        student_id = request.user.id  # Assuming the logged-in user is a student and their ID is stored in the session

        # Check if any courses were selected
        if not selected_course_ids:
            messages.error(request, 'No courses selected.')
            return redirect('course_search')

        # Iterate through the selected course IDs and register the student for each course
        for course_id in selected_course_ids:
            course = Course.objects.get(pk=course_id)
            # Check if the student is already registered for the course
            if StudentReg.objects.filter(student_id=student_id, course_id=course_id).exists():
                messages.warning(request, f'You are already registered for the course "{course.name}".')
            else:
                # Register the student for the course
                StudentReg.objects.create(student_id=student_id, course_id=course_id)
                messages.success(request, f'You have successfully registered for the course "{course.name}".')

        return redirect('course_search')

    # Redirect to the course search page if the request method is not POST
    return redirect('course_search')



def add_course(request, course_id):
    student = Student.objects.get(id=request.user.id)
    course = Course.objects.get(id=course_id)

    if request.method == 'GET':
        # Perform the course registration logic
        # This part is not included here for brevity

        return redirect('course_search')  # Redirect to course search page after successful addition

    return render(request, 'add_course.html', {'course': course})




def course_detail(request, course_id):
    course = Course.objects.get(id=course_id)
    schedules = CourseSchedule.objects.filter(course=course)
    return render(request, 'course_detail.html', {'course': course, 'schedules': schedules})

# def add_course(request):
#     if request.method == 'POST':
#         course_id = request.POST.get('course_id')
#         # Retrieve the student and course objects
#         student = Student.objects.get(id=request.user.id)  # Assuming you have a user ID in the request
#         course = Course.objects.get(id=course_id)

#         # Check if the student is already registered for the course
#         if student.courses_registered.filter(id=course_id).exists():
#             return render(request, 'add_course.html', {'error': 'You are already registered for this course.'})

#         # Check if the course has available spots
#         if course.capacity <= student.courses_registered.count():
#             return render(request, 'add_course.html', {'error': 'This course is already at full capacity.'})

#         # Add the course to the student's schedule
#         student.courses_registered.add(course)
#         return redirect('course_search')  # Redirect to course search page after successful addition

#     else:
#         return render(request, 'add_course.html')

def view_schedule(request):
    student = request.user
    registrations = StudentReg.objects.filter(student=student)
    return render(request, 'view_schedule.html', {'registrations': registrations})
