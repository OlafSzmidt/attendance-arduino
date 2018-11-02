from django.contrib import admin
from requests.models import Student, NFCCard, Event

# Register your models here.
admin.site.register(NFCCard)
admin.site.register(Student)
admin.site.register(Event)

