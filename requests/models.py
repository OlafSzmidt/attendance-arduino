from django.db import models

# Create your models here.
class NFCCard(models.Model):
    # Double check what this ID needs to be
    # make sure they are unique
    card_id = models.IntegerField()

    def __str__(self):
        return str(self.card_id)

class Student(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)

    # ENSURE duplicate NFC card cannot be set here
    # Is SET_NULL the expected behaviour for on_delete?
    nfc_card = models.ForeignKey(NFCCard, null=True, 
                                    on_delete=models.SET_NULL)
    def __str__(self):
        return self.first_name + " " + self.second_name

