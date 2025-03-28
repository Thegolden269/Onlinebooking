from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "telephone", "date_debut_booking", "heure", "date_reservation")
    search_fields = ("nom", "prenom", "telephone")
    list_filter = ("date_debut_booking",)
