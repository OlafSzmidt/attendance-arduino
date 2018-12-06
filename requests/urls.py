# pages/urls.py
from django.urls import path, include
from django.views.generic import TemplateView
from .views import (cardScanView, homePageView, myCoursesView,
                    addLecturerStaffView, viewCourseView, viewEventView,
                    addStudentAndCardView, addCourseView)

urlpatterns = [
    path('', homePageView, name='homePage'),
    path('cardScan/', cardScanView, name='cardScan'),
    path('myCourses/', myCoursesView, name='myCourses'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('addLecturer/', addLecturerStaffView, name='addLecturer'),
    path('addStudentAndCard/', addStudentAndCardView, name='addStudentAndCard'),
    path('addCourse/', addCourseView, name='addCourseView'),
    path('viewCourse/<str:course_title>/', viewCourseView, name='viewCourse'),
    path('viewEvent/<int:event_id>/', viewEventView, name='viewEvent'),
    path('addedLecturerSuccess/', TemplateView.as_view(template_name='requests/addedLecturerSuccess.html'), name='addedLecturerSuccess'),
    path('addedStudentSuccess/', TemplateView.as_view(template_name='requests/addedStudentSuccess.html'), name='addedStudentSuccess'),
]
