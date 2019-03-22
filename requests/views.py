import logging
import csv
import io
import datetime
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

logger = logging.getLogger(__name__)


def homePageView(request):
    """
    Home Page view for the website. When the user enters the website with an
    empty path (ie. /) then the home.html is rendered.
    """
    return render(request, 'requests/home.html')


@staff_member_required
def addCourseView(request):
    """
    A staff member view to add a course. If the request is a GET request; we
    render the add_course.html template and pass a django form as context. If a
    POST request is sent; we validate the data from the submitted form, read
    the contents of the csv file, create database objects and set appropriate
    relationships between course objects and lecture & lab objects. We finally
    render the template and pass students that were not found on the system
    (from the csv file) as context to be rendered.
    """
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
    """
    Staff member view to add a student object. GET request renders the template
    with two forms being passed as context (one for student objects and another
    for NFC card objects) to be filled in by the user. If the request is a POST:
    we validate the data in the forms and create appropriate objects in the Student
    and NFC Card tables. Due to database design, there is extra validation done
    when we try to add new entries to tables (another data validation feature).
    """
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
    """
    Similar to other staff member views, however this one generates a
    pseudo-random password and a random username using an algorithm designed
    in helpers.py file. Once the user and lecturer objects are created
    (and connected together); I use send an e-mail to their e-mail account
    with the credentials they provided.
    """
    if request.method == 'POST':
        # Form submitted
        submitted_form = AddANewLecturerForm(request.POST)

        if submitted_form.is_valid():
            # Create a new user account
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

            submitted_form.cleaned_data['courses_to_lead'].update(leader=lecturer)

            send_one_time_username_and_password(first_name, second_name, email,
                                                random_username, random_password)

            return HttpResponseRedirect('/addedLecturerSuccess/')
        else:
            return HttpResponse('Incorrect data submitted!')

    return render(request, 'requests/add_lecturer.html', {'form': AddANewLecturerForm})


@login_required
def addEventView(request):
    """
    A lecturer view that allows to fill in a for to create an event. Data is
    validated and passed to the database for further checks before an entry
    is made in the Event table.
    """
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
    """
    Lecturer view that shows all courses taught by the currently logged in user.
    Because there is a direct one-to-one relationship between the Lecturer and User
    tables in the database schema, we're able to filter the Lecturer table by
    entries in one column (named 'user') to correspond with the currently logged
    in user. The one result will be the lecturer object. We can then filter
    the 'Course' table to find all courses lead by this lecturer object and
    render them to the user.
    """
    logged_in_user = request.user

    # Find corresponding lecturer for this user.
    lecturer = Lecturer.objects.filter(user=logged_in_user).first()

    # Get courses only for the logged in lecturer
    courses_taught = Course.objects.filter(leader=lecturer)

    return render(request, 'requests/courses.html', {'courses': courses_taught})


@csrf_exempt
def cardScanView(request):
    """
    This view is not accessible via the browser. This is designed for the Arduino
    device to send a request with the student ID. It does queries on the database
    to find a corresponding student and then looks for courses in which the student
    is enrolled in. Using the current date and time, we then look for any events
    in the courses that are currently happening. If found, an 'Attendance' entry
    is made.
    """
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
        now = datetime.datetime.now().time()

        student_events = Event.objects.filter(course__in=student_courses)

        found_event = None

        for single_event in student_events:
            if now <= single_event.end_time and now >= single_event.start_time:
                found_event = single_event
                break

        # Mark attendance and create an object
        if found_event is None:
            return HttpResponse('404')

        query_attendance = Attendance.objects.filter(student=student, event=found_event)

        if len(query_attendance) == 0:
            attendance = Attendance.objects.create(student=student, event=found_event, attended=True)

        return HttpResponse(f'Student attendance marked. The name is {student.first_name} {student.second_name}')
    else:
        # 400 indicates incorrect syntax. We don't need a HttpResponse, this is only seen by the
        # administrator of the system so logging is sufficient.
        logger.error(f"POST data incorrect: {post_data_form.errors}")
        return HttpResponse(status=400)


@login_required
def viewCourseView(request, course_title):
    """
    Lecturer single course view. Once a lecturer clicks on one of the courses in
    the list, this view will be rendered. We find students with less than 50%
    attendance and show a filtered list of events for this course.
    """
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
    """
    Single event Lecturer view. For statistical analysis purposes, we filter
    the database here for all the students that are enrolled and the students
    that are not (or were not) present for this event. Using this, I calculate
    the students present percentage and pass it as context to the template.
    """
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
    """
    A change password view. This allows a logged in user to fill in a form
    and change their password. Their password is then stored and rehashed into
    the database in a secure form. See update_session_auth_hash().
    """
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
    """
    A helper view. Not directly accessible by browser. This view is an API view
    used by other views to obtain a CSV file of students with < 50% attendance
    as long as they pass a valid course title.
    """
    course = Course.objects.filter(title=course_title).first()
    list_of_students_under_50 = find_students_with_less_than_50_attendance(course)

    response = HttpResponse(content_type='text/csv')

    # Changes response headers to specify that a file is attached with a
    # following name.
    response['Content-Disposition'] = 'attachment; filename="under_50_{}.csv"'.format(course_title)
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Second Name'])

    for student in list_of_students_under_50:
        writer.writerow([student.first_name, student.second_name])

    return response


def export_no_attendance(request, event_course_title, event_date, event_start_time):
    """
    Another helper view, not directly accessible by the browser. Also returns a
    file as an attachment to the response with all the students not present for a
    certain event title, date and start time.
    """
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
