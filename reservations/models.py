import random
import string
import time
from django.db import models
from django.core.mail import send_mail

class Reservation(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)  # Format international possible (+33612345678)
    email = models.EmailField(null=False, blank=False)
    date_reservation = models.DateTimeField(auto_now_add=True)
    numero_reservation = models.CharField(max_length=50, unique=True, blank=True, null=True)  # Sans valeur par défaut
    date_debut_booking = models.DateField()
    heure = models.TimeField()

    def save(self, *args, **kwargs):
        # Générer un numéro de réservation unique au format 'H1550-1707896607-OUM'
        if not self.numero_reservation:  # Si numero_reservation n'est pas défini
            self.numero_reservation = self.generate_reservation_number()
        super().save(*args, **kwargs)
        

    def generate_reservation_number(self):
        """ Génère un numéro unique de réservation sous le format H1550-1707896607-OUM """
        prefix = "H1550"  # Code fixe
        timestamp = int(time.time())  # Utilisation du timestamp actuel
        suffix = self.nom[:3].upper()  # Les 3 premières lettres du nom de famille (majuscule)
        reservation_number = f"{prefix}-{timestamp}-{suffix}"
        return reservation_number


class Creneau(models.Model):
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} - {self.heure_debut} à {self.heure_fin}"