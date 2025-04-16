from datetime import datetime, timedelta, time
from django.utils.timezone import now, make_aware
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny

from .models import Reservation, Creneau
from .serializers import ReservationSerializer, CreneauSerializer

import random
import string


@api_view(['GET'])
def get_or_generate_creneaux(request):
    """Génère les créneaux pour une date donnée si inexistants, ou les retourne."""
    date_str = request.GET.get('date')
    if not date_str:
        return JsonResponse({'error': 'Paramètre "date" requis'}, status=400)

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Format de date invalide. Utilisez AAAA-MM-JJ.'}, status=400)

    existing = Creneau.objects.filter(date=date_obj)
    if not existing.exists():
        heure_debut = time(9, 0)
        heure_fin = time(17, 0)
        current_time = datetime.combine(date_obj, heure_debut)

        while current_time.time() < heure_fin:
            Creneau.objects.create(
                date=date_obj,
                heure_debut=current_time.time(),
                heure_fin=(current_time + timedelta(minutes=30)).time(),
                disponible=True
            )
            current_time += timedelta(minutes=30)

    creneaux = Creneau.objects.filter(date=date_obj).values('id', 'heure_debut', 'heure_fin', 'disponible')
    return JsonResponse({'creneaux': list(creneaux)})


class AvailableCreneauxAPIView(APIView):
    """Renvoie les créneaux disponibles pour une date donnée."""

    def get(self, request, *args, **kwargs):
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "La date est requise."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Format de date invalide."}, status=status.HTTP_400_BAD_REQUEST)

        creneaux = Creneau.objects.filter(date=date_obj, disponible=True)
        data = [
            {
                "id": c.id,
                "heure_debut": c.heure_debut.strftime("%H:%M"),
                "heure_fin": c.heure_fin.strftime("%H:%M")
            } for c in creneaux
        ]

        return Response({"creneaux_disponibles": data}, status=status.HTTP_200_OK)

available_creneaux_view = AvailableCreneauxAPIView.as_view()


class CreateReservationAPIView(APIView):
    """Crée une réservation si le créneau est disponible."""

    def post(self, request, *args, **kwargs):
        data = request.data
        creneau_id = data.get('creneau_id')
        nom = data.get('nom')
        prenom = data.get('prenom')
        email = data.get('email')

        if not all([creneau_id, nom, prenom, email]):
            return Response(
                {"error": "Tous les champs sont requis (creneau_id, nom, prenom, email)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        creneau = get_object_or_404(Creneau, id=creneau_id)

        if not creneau.disponible:
            return Response({"error": "Ce créneau est déjà réservé."}, status=status.HTTP_400_BAD_REQUEST)

        numero = self.generate_reservation_number(nom)
        reservation = Reservation.objects.create(
            creneau=creneau,
            nom=nom,
            prenom=prenom,
            email=email,
            date_debut_booking=creneau.date,
            heure=creneau.heure_debut,
            numero_reservation=numero
        )

        creneau.disponible = False
        creneau.save()

        self.send_confirmation_email(reservation)

        return Response({
            "message": "Réservation confirmée.",
            "numero_reservation": numero
        }, status=status.HTTP_201_CREATED)

    def generate_reservation_number(self, nom):
        prefix = "H1550"
        suffix = nom[:3].upper()
        random_digits = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}-{random_digits}-{suffix}"

    def send_confirmation_email(self, reservation):
        subject = "Confirmation de votre réservation"
        message = f"""
Bonjour {reservation.prenom} {reservation.nom},

Votre réservation a été confirmée pour le {reservation.date_debut_booking.strftime('%d/%m/%Y')} à {reservation.heure.strftime('%H:%M')}.
Votre numéro de réservation est : {reservation.numero_reservation}.

Merci et à bientôt,
L'équipe de réservation
"""
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [reservation.email], fail_silently=False)
        except Exception as e:
            print(f"[ERREUR ENVOI EMAIL] : {e}")

create_reservation_view = CreateReservationAPIView.as_view()


class UpdateReservationApiView(generics.UpdateAPIView):
    """Met à jour une réservation existante par son numéro."""
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_object(self):
        numero = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero)

update_reservation_view = UpdateReservationApiView.as_view()


class CancelReservationApiView(generics.DestroyAPIView):
    """Annule une réservation si la demande est faite au moins 4h avant."""
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_object(self):
        numero = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero)

    def delete(self, request, *args, **kwargs):
        reservation = self.get_object()
        reservation_time = datetime.combine(reservation.date_debut_booking, reservation.heure)

        if reservation_time.tzinfo is None:
            reservation_time = make_aware(reservation_time)

        if reservation_time - now() < timedelta(hours=4):
            return Response(
                {"error": "Vous ne pouvez annuler que jusqu'à 4 heures avant."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.send_cancellation_email(reservation)
        reservation.delete()

        return Response(
            {"message": "Réservation annulée avec succès et un email de confirmation a été envoyé."},
            status=status.HTTP_200_OK
        )

    def send_cancellation_email(self, reservation):
        subject = f"Annulation de votre réservation #{reservation.numero_reservation}"
        message = f"""
Bonjour {reservation.prenom} {reservation.nom},

Votre réservation #{reservation.numero_reservation} a été annulée avec succès.

Merci pour votre compréhension.
"""
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, [reservation.email], fail_silently=False)
        except Exception as e:
            print(f"[ERREUR ENVOI EMAIL] : {e}")

cancel_reservation_view = CancelReservationApiView.as_view()


class RetrieveReservationApiView(generics.RetrieveAPIView):
    """Récupère une réservation à partir de son numéro."""
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_object(self):
        numero = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero)

retrieve_reservation_view = RetrieveReservationApiView.as_view()

