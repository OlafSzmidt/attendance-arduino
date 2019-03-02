import logging
import csv
import io
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from requests.forms import (ScanCardValidationForm, AddANewLecturerForm,
                            AddANewStudentForm, AddANFCCardForm, AddCourseForm,
                            AddEventForm)
from requests.models import (Student, Lecturer, NFCCard, Event, Attendance,
                             Course)
from requests.helpers import (generate_random_username,
                              calculate_percentage_attendance_for_event,
                              send_one_time_username_and_password,
                              find_students_with_less_than_50_attendance,
                              find_students_not_present_for_event)

# Get an instance of a logger
logger = logging.getLogger(__name__)

def homePageView(request):
    return render(request, 'requests/home.html')

@staff_member_required
def addCourseView(request):
    if request.method == 'POST':
        # Form submitted
        course_form = AddCourseForm(request.POST, request.FILES)
        line_counter = 0
        students_from_csv = []
        students_not_found = []

        if course_form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8')
            io_string = io.StringIO(decoded_file)
            csv_reader = csv.reader(io_string, delimiter=',')

            # TODO: check if this actually works, trouble finding students...
            for row in csv_reader:
                if line_counter == 0:
                    line_counter += 1
                    pass
                else:
                    student = Student.objects.filter(first_name=row[0], second_name=row[1]).first()
                    if student is None:
                        students_not_found.append(str(row[0]) + ' ' + str(row[1]))
                    else:
                        students_from_csv.append(student)

                    line_counter += 1

            course = Course.objects.create(title=course_form.cleaned_data['title'],
                                           leader=course_form.cleaned_data['leader']
                                           )

            course.lectures.set(course_form.cleaned_data['lectures'])
            course.labs.set(course_form.cleaned_data['labs'])

            if len(students_from_csv) > 0:
                course.students.set(students_from_csv)

            course.save()

            return render(request, 'requests/addedCourseSuccess.html', {'students_not_found': students_not_found})
        else:
            print(course_form.errors)
            return HttpResponse("Invalid data submitted!")
    return render(request, 'requests/add_course.html',  {'form': AddCourseForm})

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

            first_name = submitted_form.cleaned_data['first_name']
            second_name = submitted_form.cleaned_data['second_name']
            email = submitted_form.cleaned_data['email']

            # User created, now a lecturer object
            lecturer = Lecturer.objects.create(first_name=first_name,
                                               second_name=second_name,
                                               user=new_user, email=email)

            send_one_time_username_and_password(first_name, second_name, email,
                                                random_username, random_password)

            return HttpResponseRedirect('/addedLecturerSuccess/')
        else:
            return HttpResponse('Incorrect data submitted!')

    return render(request, 'requests/add_lecturer.html', {'form': AddANewLecturerForm})

@login_required
def addEventView(request):
    if request.method == 'POST':
        # form submitted
        submitted_form = AddEventForm(request.POST)

        if submitted_form.is_valid():
            event = Event.objects.create(date=submitted_form.cleaned_data['date'],
                                         start_time=submitted_form.cleaned_data['start_time'],
                                         end_time=submitted_form.cleaned_data['end_time'],
                                         notes=submitted_form.cleaned_data['notes'],
                                         course=submitted_form.cleaned_data['course'])
            return HttpResponseRedirect('/addedEventSuccess/')
        else:
            return HttpResponse('Incorrect data submitted!')

    return render(request, 'requests/add_event.html', {'form': AddEventForm})

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

    request_data = {'card_id': str(request.body, 'utf-8')}
    # Create a form to validate incoming data.
    # This will check key names, key types, value types.
    post_data_form = ScanCardValidationForm(request_data)
    if post_data_form.is_valid():
        # Find student using the card ID
        student = Student.objects.filter(nfccard__card_id=request_data['card_id']).first()
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
    students_less_than_50 = find_students_with_less_than_50_attendance(course)

    return render(request, 'requests/single_course.html', {'course': course,
                                                           'lecture_halls': course.lectures.all(),
                                                           'lab_halls': course.labs.all(),
                                                           'events': events,
                                                           'less_than_50': students_less_than_50,
                                                           }
                 )

@login_required
def viewEventView(request, event_id):
    event = Event.objects.filter(id=event_id).first()
    students_enrolled = event.course.students.all().count()
    students_not_present = find_students_not_present_for_event(event)

    stats = {
        'students_enrolled': students_enrolled,
        'students_not_present': students_not_present,
        'students_marked_present': calculate_percentage_attendance_for_event(event)['number'],
        'students_present_percentage': calculate_percentage_attendance_for_event(event)['percentage'],
        }

    return render(request, 'requests/single_event.html', {'event': event, 'stats': stats})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('homePage')
        else:
            messages.error(request, 'Please correct the error.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'requests/change_password.html', {
        'form': form
    })


def export_under_50_csv(request, course_title):
    course = Course.objects.filter(title=course_title).first()
    list_of_students_under_50 = find_students_with_less_than_50_attendance(course)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="under_50_{}.csv"'.format(course_title)
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Second Name'])

    for student in list_of_students_under_50:
        writer.writerow([student.first_name, student.second_name])

    return response


def export_no_attendance(request, event_course_title, event_date, event_start_time):
    # Find all courses matching the title of the course. Returns a queryset.
    course = Course.objects.filter(title=event_course_title).first()

    # Based on the queryset and other date/time information, find the event.
    event = Event.objects.filter(date=event_date, start_time=event_start_time,
                                  course=course).first()

    students_not_found = find_students_not_present_for_event(event)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students_not_present_{}.csv"'.format(event_course_title)
    writer = csv.writer(response)
    writer.writerow(['Student Full Name'])

    for student in students_not_found:
        writer.writerow([student])

    return response
