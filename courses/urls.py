from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('course_search/', views.course_search, name='course_search'),
    path('course_detail/<int:course_id>/', views.course_detail, name='course_detail'),
    path('add_course/<int:course_id>/', views.add_course, name='add_course'),
    path('view_schedule/', views.view_schedule, name='view_schedule'),
]
