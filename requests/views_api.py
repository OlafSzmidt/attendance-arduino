from rest_framework.views import APIView
from rest_framework.response import Response
from requests.models import (Event, Attendance, Course)
from .helpers import calculate_percentage_attendance_for_event
class CourseAttendanceData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):

        course = Course.objects.filter(id=int(request.GET['courseid'])).first()
        course_events = list(Event.objects.filter(course=course))
        event_labels = []
        event_data = []

        for event in course_events:
            event_labels.append(event.date)
            event_data.append(calculate_percentage_attendance_for_event(event))

        data = {
            "labels": event_labels,
            "attendance": event_data
        }

        return Response(data)
