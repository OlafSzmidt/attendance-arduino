import datetime
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
            event_data.append(calculate_percentage_attendance_for_event(event)['percentage'])

        data = {
            "labels": event_labels,
            "attendance": event_data
        }

        return Response(data)

class EventTimeScannedData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        event = Event.objects.filter(id=int(request.GET['eventid'])).first()
        # Based on the length of the event, find the equivalent time to be
        # equal of 20% of the event time to use as one entry in the bar graph.
        start_time = event.start_time
        end_time = event.end_time
        start_td = datetime.timedelta(hours=start_time.hour,
                                      minutes=start_time.minute,
                                      seconds=start_time.second,
                                      microseconds=start_time.microsecond)

        end_td = datetime.timedelta(hours=end_time.hour,
                                    minutes=end_time.minute,
                                    seconds=end_time.second,
                                    microseconds=end_time.microsecond)

        difference = (end_td - start_td).total_seconds() / 5

        low_bracket_time = datetime.datetime(event.date.year,
                                             event.date.month,
                                             event.date.day,
                                             start_time.hour,
                                             start_time.minute,
                                             start_time.second)

        result_data = []

        for i in range(5):
            top_bracket_time = low_bracket_time + datetime.timedelta(seconds=difference)

            attendances_in_range = Attendance.objects.filter(event=event,
                                                             scanned_at__gte=low_bracket_time,
                                                             scanned_at__lt=top_bracket_time).count()

            result_data.append(attendances_in_range)

            low_bracket_time = top_bracket_time

        labels = ["0-20%, 20-40%, 40-60%, 60-80%, 80-100%"]

        return Response({
            'labels': labels,
            'attendance_data': result_data
        })
