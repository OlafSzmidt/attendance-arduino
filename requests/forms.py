from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from .models import Lecturer, Course, Student, NFCCard, Event


class ScanCardValidationForm(forms.Form):
    """
    A form only used internally when a student ID card gets scanned. Form
    functionality allows for easy validation of the data passed in, so incorrect
    data passed by the arduino can be rejected easily.
    """
    card_id = forms.CharField()

    def is_valid(self):

        # Run parent validation first
        valid = super(ScanCardValidationForm, self).is_valid()

        if not valid:
            return valid

        # First check if card_id key exists with a right type
        try:
            id_provided = self.cleaned_data['card_id']
        except KeyError:
            self._errors['no_card_id'] = 'Card ID key not provided in the POSTed data.'
            return False

        return True


class AddANewLecturerForm(forms.ModelForm):
    """
    A form used when a new lecturer is being added. Because of good database design,
    most fields can be passed directly as Meta from the database and don't have
    to be created manually. Attribute classes from Bootstrap 4 are entered here.
    Courses_to_lead is a multiple checkbox option that finds all courses that have
    null leaders (ie. are free to be picked up by a new Lecturer).
    """
    class Meta:
        model = Lecturer
        fields = ['first_name' , 'second_name', 'email']
        widgets = {
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'second_name': forms.TextInput(attrs={'class': 'form-control'}),
                'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    courses_to_lead = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Course.objects.exclude(leader__isnull=False), required=False)


class AddANewStudentForm(forms.ModelForm):
    """
    A new student form. Uses fields directly from the Student table and adds them
    as TextInput objects. Custom bootstrap 4 styling added.
    """
    class Meta:
        model = Student
        fields = ['first_name', 'second_name']
        widgets = {
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'second_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddANFCCardForm(forms.ModelForm):
    """
    A new NFC Card form. Uses a card_id field directly from the NFCCard table and
    add it as a TextInput object. Custom bootstrap 4 styling added.
    """
    class Meta:
        model = NFCCard
        fields = ['card_id']
        widgets = {
                'card_id': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AddEventForm(forms.ModelForm):
    """
    A new Event form. Uses fields directly from the Event table and adds them
    as TextInput, TimeInput and Select objects. Custom bootstrap 4 styling added.

    Also adds a date to be chosen. An external library bootstrap_datepicker_plus
    provides a DatePickerInput that was ideal for the purpose here.
    """
    class Meta:
        model = Event
        fields = ['date', 'start_time', 'end_time', 'notes', 'course']
        widgets = {
                'date': DatePickerInput(),
                'start_time': forms.TimeInput(attrs={'class': 'form-control'}),
                'end_time': forms.TimeInput(attrs={'class': 'form-control'}),
                'notes': forms.TextInput(attrs={'class': 'form-control'}),
                'course': forms.Select(attrs={'class': 'form-control'}),
        }


class AddCourseForm(forms.ModelForm):
    """
    A new Course form. Mostly similar to all other forms above with the
    difference that there is a SelectMultiple object used for lectures and labs.
    Also, a csv file is passed through a FileField().
    """
    class Meta:
        model = Course
        fields = ['title', 'leader', 'lectures', 'labs']
        widgets = {
                'title': forms.TextInput(attrs={'class': 'form-control'}),
                'leader': forms.Select(attrs={'class': 'form-control'}),
                'lectures': forms.SelectMultiple(attrs={'class': 'form-control'}),
                'labs': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    file = forms.FileField()
