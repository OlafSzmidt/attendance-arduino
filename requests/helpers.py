from random import choice
from string import ascii_lowercase, digits
from django.contrib.auth.models import User
from .models import Attendance

def generate_random_username(length=16, chars=ascii_lowercase+digits, split=4, delimiter='-'):

    username = ''.join([choice(chars) for i in range(length)])

    if split:
        username = delimiter.join([username[start:start+split] for start in range(0, len(username), split)])

    try:
        User.objects.get(username=username)
        return generate_random_username(length=length, chars=chars, split=split, delimiter=delimiter)
    except User.DoesNotExist:
        return username;

def calculate_percentage_attendance_for_event(event):
    attendances = Attendance.objects.filter(event=event)
    students_enrolled = event.course.students.all().count()
    students_marked_present = 0
    for attendance in attendances:
        if(attendance.attended):
            students_marked_present += 1

    if students_marked_present == 0:
        return {
            'number': students_marked_present,
            'percentage': 0,
        }
    else:
        return {
            'number': students_marked_present,
            'percentage': students_enrolled / students_marked_present * 100,
        }
