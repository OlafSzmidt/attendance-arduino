# Generated by Django 2.1.2 on 2018-12-05 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0007_auto_20181205_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='lectures',
            field=models.ManyToManyField(to='requests.LectureHall'),
        ),
    ]
