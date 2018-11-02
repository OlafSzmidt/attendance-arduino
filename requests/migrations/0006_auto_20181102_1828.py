# Generated by Django 2.1 on 2018-11-02 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0005_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_time',
            field=models.TimeField(help_text='End time', verbose_name='End time'),
        ),
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.TextField(help_text='Event notes or comments', verbose_name='Event notes or comments'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_time',
            field=models.TimeField(help_text='Starting time', verbose_name='Starting time'),
        ),
    ]
