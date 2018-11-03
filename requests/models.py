from django import forms
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name + " " + self.second_name

    class Meta:
        abstract = True

class Student(Person):
    '''Subclass of Person, no added functionality.'''

class Lecturer(Person):
    '''Subclass of Person, no added functionality.'''

class Course(models.Model):
    title = models.CharField(max_length=40)
    leader = models.ForeignKey(Lecturer, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.title

class NFCCard(models.Model):
    card_id = models.IntegerField()
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.card_id} ({self.student.first_name} {self.student.second_name})'

class Event(models.Model):
    date = models.DateField(u'Date of the event', help_text=u'YYYY:MM:DD')
    start_time = models.TimeField(u'Starting time', help_text=u'HH:MM')
    end_time = models.TimeField(u'End time', help_text=u'HH:MM')
    notes = models.TextField(u'Event notes or comments', help_text=u'Event notes or comments')
    course = models.ForeignKey(Course, blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.course.title} ({self.date} {self.start_time})'
