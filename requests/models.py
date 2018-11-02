from django import forms
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name + " " + self.second_name

class Student(Person):
    '''Subclass of Person, no added functionality.'''

class Lecturer(Person):
    '''Subclass of Person, no added functionality.'''

class Course(models.Model):
    title = models.CharField(max_length=40)
    leader = models.ForeignKey(Lecturer, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student, null=False)

    def __str__(self):
        return self.title

class NFCCard(models.Model):
    # TODO: Double check what this ID needs to be  make sure they are unique
    card_id = models.IntegerField()
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.card_id)

class Event(models.Model):
    name = models.ChartField(max_length=100)
    date = models.DateField(u'Date of the event', help_text=u'YYYY:MM:DD')
    start_time = models.TimeField(u'Starting time', help_text=u'HH:MM')
    end_time = models.TimeField(u'End time', help_text=u'HH:MM')
    notes = models.TextField(u'Event notes or comments', help_text=u'Event notes or comments')
    
    # HOW TO CONNECT THIS TO COURSE? MANY EVENTS TO SINGLE COURSE OBJECT. FOREIGN KEY WHICH WAY?
    
    # Validation ideas:
    # end time cant be before start time. 
    # Is course lecturer the admin of this event?
    # Complicated: does a student have a clash at this point?