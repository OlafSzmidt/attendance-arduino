# pages/urls.py
from django.urls import path

from .views import cardScanView, homePageView

urlpatterns = [
    path('', homePageView, name='homePage'),
    path('cardScan/', cardScanView, name='cardScan')
]