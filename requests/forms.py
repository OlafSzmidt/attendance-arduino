from django import forms

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
