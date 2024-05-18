from django.urls import path
from . import views
from .views import login_or_register,course_search,register_courses,add_course

urlpatterns = [
    path('', views.login_or_register, name='login_or_register'),  # Add this line
    path('course_search/', views.course_search, name='course_search'),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('register_courses/', register_courses, name='register_courses'),
    path('add_course/<int:course_id>/', views.add_course, name='add_course'),
    path('view_schedule/', views.view_schedule, name='view_schedule'),
]