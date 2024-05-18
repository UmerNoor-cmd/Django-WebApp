# courses/forms.py
from django import forms
from .models import Student

class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['name', 'email', 'password']


class CourseAddForm(forms.Form):
    course_id = forms.IntegerField(label='Course ID', required=True)