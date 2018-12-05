import logging
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from requests.forms import ScanCardValidationForm, AddANewLecturerForm, AddANewStudentForm, AddANFCCardForm
from requests.models import Student, Lecturer, NFCCard, Event, Attendance, Course
from requests.helpers import generate_random_username

# Get an instance of a logger
logger = logging.getLogger(__name__)

def homePageView(request):
    return render(request, 'requests/home.html')

@staff_member_required
def addStudentAndCardView(request):
    if request.method == 'POST':
        # Form submitted
        student_form = AddANewStudentForm(request.POST)
        nfc_form = AddANFCCardForm(request.POST)

        if student_form.is_valid() and nfc_form.is_valid():
            student = Student.objects.create(first_name=student_form.cleaned_data['first_name'],
                                             second_name=student_form.cleaned_data['second_name'])
            nfc_card = NFCCard.objects.create(card_id=nfc_form.cleaned_data['card_id'],
                                              student=student)

            return HttpResponseRedirect('/addedStudentSuccess/')
        else:
            return HttpResponse('Incorrect data submitted!')

    return render(request, 'requests/add_students_and_cards.html', {'student_form': AddANewStudentForm, 'nfc_form': AddANFCCardForm})

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
            new_user = User.objects.create_user(username=random_username,
                                                password=random_password)

            # User created, now a lecturer object
            lecturer = Lecturer.objects.create(first_name=submitted_form.cleaned_data['first_name'],
                                               second_name=submitted_form.cleaned_data['second_name'],
                                               user=new_user)

            return HttpResponseRedirect('/addedLecturerSuccess/')
        else:
            return HttpResponse('Incorrect data submitted!')

    return render(request, 'requests/add_lecturer.html', {'form': AddANewLecturerForm})

@login_required
def myCoursesView(request):
    logged_in_user = request.user

    # Find corresponding lecturer
    lecturer = Lecturer.objects.filter(user=logged_in_user).first()

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
        student_courses = Course.objects.filter(students=student)
        logger.info(f'Student courses found: {student_courses}')

        # Find the event that the student is enrolling for
        student_event = Event.objects.filter(course__in=student_courses)

        # Mark attendance and create an object
        attendance = Attendance.objects.create(student=student, event=student_event.first(), attended=True)

        return HttpResponse(f'Student attendance marked. The name is {student.first_name} {student.second_name}')
    else:
        # 400 indicates incorrect syntax. We don't need a HttpResponse, this is only seen by the
        # administrator of the system so logging is sufficient.
        logger.error(f"POST data incorrect: {post_data_form.errors}")
        return HttpResponse(status=400)

@login_required
def viewCourseView(request, course_title):
    course = Course.objects.filter(title=course_title).first()
    events = Event.objects.filter(course=course)
    return render(request, 'requests/single_course.html', {'course': course, 'lecture_halls': course.lectures.all(), 'lab_halls': course.labs.all(), 'events': events})

@login_required
def viewEventView(request, event_id):
    event = Event.objects.filter(id=event_id).first()
    return render(request, 'requests/single_event.html', {'event': event})
