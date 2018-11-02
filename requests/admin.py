from django.contrib import admin
from requests.models import (Student, NFCCard, 
                            Event, Lecturer, Course)

# Register your models here.
admin.site.register(NFCCard)
admin.site.register(Student)
admin.site.register(Lecturer)
admin.site.register(Course)
admin.site.register(Event)

