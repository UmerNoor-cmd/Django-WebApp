from django.urls import path
from . import views
from .views import login_or_register,course_search,add_course,course_detail

urlpatterns = [
    path('', views.login_or_register, name='login_or_register'),  # Add this line
    path('course_search/', views.course_search, name='course_search'),
    path('generate_reports/', views.generate_reports, name='generate_reports'),  # Add this line
    path('course_detail/', views.course_detail, name='course_detail'),
    path('add_course/', add_course, name='add_course'),
    
]