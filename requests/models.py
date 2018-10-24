from django.db import models

# Create your models here.
class Student(models.Model):
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)

    def __str__(self):
        return self.first_name + " " + self.second_name

class NFCCard(models.Model):
    # Double check what this ID needs to be
    # make sure they are unique
    card_id = models.IntegerField()
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.card_id)
