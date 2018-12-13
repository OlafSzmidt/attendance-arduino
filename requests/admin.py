from django.contrib import admin
from requests.models import (Student, NFCCard, Event, Lecturer, Course,
                             Attendance, LectureHall, LaboratoryHall)

class AttendanceAdmin(admin.ModelAdmin):
    readonly_fields = ('scanned_at',)


# Register your models here.
admin.site.register(NFCCard)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Course)
admin.site.register(Event)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(LectureHall)
admin.site.register(LaboratoryHall)
