from django.contrib import admin
from .models import Reservation, Creneau

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "telephone", "date_debut_booking", "heure", "date_reservation")
    search_fields = ("nom", "prenom", "telephone")
    list_filter = ("date_debut_booking",)

class CreneauAdmin(admin.ModelAdmin):
    list_display = ("date", "heure_debut", "heure_fin", "disponible")
    search_fields = ("date",)
    list_filter = ("disponible",)
    
admin.site.register(Creneau, CreneauAdmin)