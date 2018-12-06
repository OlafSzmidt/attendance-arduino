from django import forms
from .models import Lecturer, Course, Student, NFCCard, Event

class ScanCardValidationForm(forms.Form):
    card_id = forms.IntegerField()

    def is_valid(self):

        # Run parent validation first
        valid = super(ScanCardValidationForm, self).is_valid()

        # Is it valid?
        if not valid:
            return valid

        # TODO: check if card_id correlates to DB entry. Make github issue
        # TODO: check all types and vals
        # TODO; check all names

        # First check if card_id key exists with a right type
        try:
            id_provided = self.cleaned_data['card_id']
            if not isinstance(id_provided, int):
                # TODO: more checking here for correct ID once we know what it is
                self._errors['card_id_invalid_type'] = 'Card ID value provided is not an integer.'
                return False
        except KeyError:
            self._errors['no_card_id'] = 'Card ID key not provided in the POSTed data.'
            return False

        return True


class AddANewLecturerForm(forms.ModelForm):
    class Meta:
        model = Lecturer
        fields = ['first_name' , 'second_name']
        widgets = {
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'second_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    courses_to_lead = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Course.objects.all())

class AddANewStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'second_name']
        widgets = {
                'first_name': forms.TextInput(attrs={'class': 'form-control'}),
                'second_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AddANFCCardForm(forms.ModelForm):
    class Meta:
        model = NFCCard
        fields = ['card_id']
        widgets = {
                'card_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AddEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['date', 'start_time', 'end_time', 'notes', 'course']
        widgets = {
                'date': forms.SelectDateWidget(attrs={'class': 'form-control'}),
                'start_time': forms.TimeInput(attrs={'class': 'form-control'}),
                'end_time': forms.TimeInput(attrs={'class': 'form-control'}),
                'notes': forms.TextInput(attrs={'class': 'form-control'}),
                'course': forms.Select(attrs={'class': 'form-control'}),
        }

class AddCourseForm(forms.ModelForm):
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
