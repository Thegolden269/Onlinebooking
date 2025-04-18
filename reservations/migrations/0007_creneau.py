# Generated by Django 5.1.7 on 2025-03-27 23:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0006_alter_reservation_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Creneau',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('heure_debut', models.TimeField()),
                ('heure_fin', models.TimeField()),
                ('disponible', models.BooleanField(default=True)),
            ],
        ),
    ]
