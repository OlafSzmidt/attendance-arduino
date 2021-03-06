import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from requests.models import (Event, Attendance, Course)
from .helpers import calculate_percentage_attendance_for_event

class CourseAttendanceData(APIView):
    """
    Custom APIView used by a template graph. When a course template is rendered,
    a GET request is sent to this API endpoint with a 'courseid' as a parameter.
    Attendance is calculate and returned as JSON to be rendered by the template
    modules.
    """
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
    """
    Custom APIView used by a template graph. When an event template is rendered,
    a GET request is sent to this API endpoint with a 'eventid' as a parameter.
    It uses time delta's to calculate "brackets" of time in which students have
    signed their attendance in the event. It then returns those as a JSON to the
    template to be rendered appropriately.
    """
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
        students_found_so_far = 0

        for i in range(5):
            top_bracket_time = low_bracket_time + datetime.timedelta(seconds=difference)

            attendances_in_range = Attendance.objects.filter(event=event,
                                                             scanned_at__gte=low_bracket_time,
                                                             scanned_at__lt=top_bracket_time).count()

            students_found_so_far += attendances_in_range

            result_data.append(attendances_in_range)

            low_bracket_time = top_bracket_time

        manually_marked = Attendance.objects.filter(event=event).count() - students_found_so_far
        result_data.append(manually_marked)

        labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%", "Manually Marked"]

        return Response({
            'labels': labels,
            'attendance_data': result_data
        })
