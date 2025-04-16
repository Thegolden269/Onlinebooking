from django.db import models

class Creneau(models.Model):
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.date} - {self.heure_debut} à {self.heure_fin}"

class Reservation(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, blank=False, null=False)
    date_reservation = models.DateTimeField(auto_now_add=True)
    numero_reservation = models.CharField(max_length=50, unique=True)
    date_debut_booking = models.DateField()
    heure = models.TimeField()
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.numero_reservation} - {self.prenom} {self.nom}"
