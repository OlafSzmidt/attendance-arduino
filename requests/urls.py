# pages/urls.py
from django.urls import path, include
from .views import cardScanView, homePageView, myCoursesView

urlpatterns = [
    path('', homePageView, name='homePage'),
    path('cardScan/', cardScanView, name='cardScan'),
    path('myCourses/', myCoursesView, name='myCourses'),
    path('accounts/', include('django.contrib.auth.urls')),
]
