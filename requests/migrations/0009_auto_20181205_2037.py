# Generated by Django 2.1.2 on 2018-12-05 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0008_auto_20181205_2032'),
    ]

    operations = [
        migrations.CreateModel(
            name='LaboratoryHall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=12)),
            ],
        ),
        migrations.AlterField(
            model_name='lecturehall',
            name='name',
            field=models.CharField(max_length=12),
        ),
        migrations.AddField(
            model_name='course',
            name='labs',
            field=models.ManyToManyField(to='requests.LaboratoryHall'),
        ),
    ]