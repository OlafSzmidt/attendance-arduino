# pages/urls.py
from django.urls import path, include
from django.views.generic import TemplateView
from .views import (cardScanView, homePageView, myCoursesView,
                    addLecturerStaffView, viewCourseView, viewEventView,
                    addStudentAndCardView, addCourseView, addEventView,
                    change_password_view, export_under_50_csv, export_no_attendance)
from .views_api import CourseAttendanceData, EventTimeScannedData


# Entry point of the application. Runs a regex pattern match to see if the path of
# the URL matches any specified in the list below. If it does, a connected view is
# rendered.

urlpatterns = [
    path('', homePageView, name='homePage'),
    path('cardScan/', cardScanView, name='cardScan'),
    path('myCourses/', myCoursesView, name='myCourses'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('addLecturer/', addLecturerStaffView, name='addLecturer'),
    path('addStudentAndCard/', addStudentAndCardView, name='addStudentAndCard'),
    path('addCourse/', addCourseView, name='addCourseView'),
    path('addEvent/', addEventView, name='addEvent'),
    path('viewCourse/<str:course_title>/', viewCourseView, name='viewCourse'),
    path('viewEvent/<int:event_id>/', viewEventView, name='viewEvent'),
    path('addedLecturerSuccess/', TemplateView.as_view(template_name='requests/addedLecturerSuccess.html'), name='addedLecturerSuccess'),
    path('addedStudentSuccess/', TemplateView.as_view(template_name='requests/addedStudentSuccess.html'), name='addedStudentSuccess'),
    path('addedEventSuccess/', TemplateView.as_view(template_name='requests/addedEventSuccess.html'), name='addedEventSuccess'),
    path('changePassword/', change_password_view, name='change_password'),
    path('exportCsv/<str:course_title>/', export_under_50_csv, name='exportUnder50'),
    path('exportNoAttendance/<str:event_course_title>/<str:event_date>/<str:event_start_time>', export_no_attendance, name='exportNoAttendance'),
    path('api/course/attendanceHistory/', CourseAttendanceData.as_view()),
    path('api/event/whenDoStudentsMark/', EventTimeScannedData.as_view()),
]
