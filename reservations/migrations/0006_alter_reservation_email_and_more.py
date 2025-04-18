# Generated by Django 5.1.7 on 2025-03-27 22:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0005_alter_reservation_numero_reservation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='numero_reservation',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
