import logging
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from requests.forms import ScanCardValidationForm, AddANewLecturerForm
from requests.models import Student, Lecturer, NFCCard, Event, Attendance, Course
from requests.helpers import generate_random_username

# Get an instance of a logger
logger = logging.getLogger(__name__)

def homePageView(request):
    return render(request, 'requests/home.html')

@staff_member_required
def addLecturerStaffView(request):
    if request.method == 'POST':
        # Form submitted
        submitted_form = AddANewLecturerForm(request.POST)

        if submitted_form.is_valid():
            # Create a new user account
            # TODO: add email to user and then send emails with credentials
            random_username = generate_random_username(length=6)
            random_password = User.objects.make_random_password()
            logger.info(f'Random username generated: {random_username}')
            new_user = User.objects.create_user(username=random_username, password=random_password)

            # User created, now a lecturer object
            lecturer = Lecturer.objects.create(first_name=submitted_form.cleaned_data['first_name'],
                                               second_name=submitted_form.cleaned_data['second_name'],
                                               user=new_user)

    return render(request, 'requests/add_lecturer.html', {'form': AddANewLecturerForm})

def myCoursesView(request):
    # Just presume the first lecturer is logged in for now
    # TODO: once logging in is added, add a check here
    lecturer = Lecturer.objects.all().first()

    # Get courses only for the logged in lecturer
    courses_taught = Course.objects.filter(leader=lecturer)

    return render(request, 'requests/courses.html', {'courses': courses_taught})

@csrf_exempt
def cardScanView(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    # Create a form to validate incoming data.
    # This will check key names, key types, value types.
    post_data_form = ScanCardValidationForm(request.POST)
    if post_data_form.is_valid():
        # Find student using the card ID
        student = Student.objects.filter(nfccard__card_id=request.POST['card_id']).first()
        if student is None:
            return HttpResponse('No student found!')

        logger.info(f'Student found! The name is {student.first_name} {student.second_name}')

        # Get all courses student is enrolled in
        # TODO: do some checks here if student courses is empty
        student_courses = Course.objects.filter(students=student)
        logger.info(f'Student courses found: {student_courses}')

        # Find the event that the student is enrolling for
        # TODO: find some grace periods after and before. What if a lecture is straight after?
        # TODO: Filter student events based on start_time, end_time and current time as well as student courses above
        # TODO: check for no events returned? check if more than 1, return error, log it
        student_event = Event.objects.filter(course__in=student_courses)

        # TODO: now use the Attendance model to mark the student's event and student as present.
        # Mark attendance and create an object
        attendance = Attendance.objects.create(student=student, event=student_event.first(), attended=True)

        return HttpResponse(f'Student attendance marked. The name is {student.first_name} {student.second_name}')
    else:
        # 400 indicates incorrect syntax. We don't need a HttpResponse, this is only seen by the
        # administrator of the system so logging is sufficient.
        logger.error(f"POST data incorrect: {post_data_form.errors}")
        return HttpResponse(status=400)
