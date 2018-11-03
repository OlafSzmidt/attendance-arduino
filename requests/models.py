from django import forms
from django.db import models
from django.core.validators import RegexValidator

class Person(models.Model):
    '''Abstract model to be inherited by Student or Lecturer'''
    first_name = models.CharField(max_length=30,
                                  validators=[
                                    RegexValidator(
                                        regex='^[a-zA-Z]+$',
                                        message='First name needs to only ' +
                                        'contain standard letters.',
                                        code='invalid_firstname')
                                  ]
                                  )
    second_name = models.CharField(max_length=30,
                                   validators=[
                                     RegexValidator(
                                         regex='^[a-zA-Z]+$',
                                         message='Second name needs to only ' +
                                         'contain standard letters.',
                                         code='invalid_secondname')
                                   ]
                                   )

    def __str__(self):
        return self.first_name + " " + self.second_name

    class Meta:
        abstract = True

class Student(Person):
    '''Subclass of Person, no added functionality.'''

class Lecturer(Person):
    '''Subclass of Person, no added functionality.'''

class Course(models.Model):
    '''Course which is being taught by a single lecturer and attended by many
    students. Not to be confused with Event.'''
    title = models.CharField(max_length=40)
    leader = models.ForeignKey(Lecturer, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student)

    def __str__(self):
        return self.title

class NFCCard(models.Model):
    '''An NFC card which is being scanned by the arduino and is connected to a
    single student'''
    card_id = models.IntegerField()
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.card_id} ({self.student.first_name} {self.student.second_name})'

class Event(models.Model):
    '''A single event occurance of a Course at a particular date and time'''
    date = models.DateField(u'Date of the event', help_text=u'YYYY:MM:DD')
    start_time = models.TimeField(u'Starting time', help_text=u'HH:MM')
    end_time = models.TimeField(u'End time', help_text=u'HH:MM')
    notes = models.TextField(u'Event notes or comments', help_text=u'Event notes or comments')
    course = models.ForeignKey(Course, blank=False, null=False, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.course.title} ({self.date} {self.start_time})'

class Attendance(models.Model):
    '''Attendance model is used to output results once students have marked
    themselves'''
    student = models.ForeignKey(Student)
    event = models.ForeignKey(Event)
    attended = models.BooleanField(default=False)
    
