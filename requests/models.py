from django import forms
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Person(models.Model):
    '''
    Abstract model (cannot be created directly) to be inherited by Student or
    Lecturer. Database uniqueness is set by two columns together (first_name and
    second_name). Both columns are validated by Regex rules when data is passed
    in; and they have a maximum length validation.
    '''
    class Meta:
        unique_together = ["first_name", "second_name"]

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
    '''
    Subclass of Person, no added functionality.
    '''


class Lecturer(Person):
    '''
    Subclass of Person, difference in functionality from Student is that
    these objects have a 1-1 relationship with a User and an email field.
    '''
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    email = models.EmailField()


class LectureHall(models.Model):
    '''
    A LectureHall model is created alongside a Course to be viewed under
    teaching locations.
    '''
    name = models.CharField(max_length=12, null=False)

    def __str__(self):
        return self.name


class LaboratoryHall(models.Model):
    '''
    A LaboratoryHall model is created alongside a Course to be viewed under
    teaching locations.
    '''
    name = models.CharField(max_length=12, null=False)

    def __str__(self):
        return self.name


class Course(models.Model):
    '''
    Course which is being taught by a single lecturer and attended by many
    students. Not to be confused with Event.
    '''
    title = models.CharField(max_length=40)
    leader = models.ForeignKey(Lecturer, blank=True, null=True, on_delete=models.SET_NULL)
    students = models.ManyToManyField(Student, blank=True)
    lectures = models.ManyToManyField(LectureHall, blank=False)
    labs = models.ManyToManyField(LaboratoryHall, blank=False)

    def __str__(self):
        return self.title


class NFCCard(models.Model):
    '''
    An NFC card which is being scanned by the arduino and is connected to a
    single (1-to-1 relationship) student.
    '''
    card_id = models.CharField(null=False, unique=True, max_length=21)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.card_id} ({self.student.first_name} {self.student.second_name})'


class Event(models.Model):
    '''
    A single event occurance of a Course at a particular date and time.
    '''
    date = models.DateField(u'Date of the event', help_text=u'YYYY:MM:DD')
    start_time = models.TimeField(u'Starting time', help_text=u'HH:MM')
    end_time = models.TimeField(u'End time', help_text=u'HH:MM')
    notes = models.TextField(u'Event notes or comments', help_text=u'Event notes or comments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.course.title} ({self.date} {self.start_time})'

    def __unicode__(self):
        return f'{self.course.title} ({self.date} {self.start_time})'

class Attendance(models.Model):
    '''
    Attendance model is used to output results once students have marked
    themselves. Uses the student and event as foreign keys.
    '''
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    scanned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student} ({self.event})'
