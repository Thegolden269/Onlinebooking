from django.utils.timezone import now
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Reservation
from .serializers import ReservationSerializer
from django.core.mail import send_mail
from django.conf import settings

from django.utils.timezone import make_aware

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Creneau

from rest_framework.permissions import AllowAny




class AvailableCreneauxAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Récupérer la date passée en paramètre dans l'URL
        date_selectionnee = request.query_params.get("date")  # Exemple de paramètre date=2025-03-28
        
        if not date_selectionnee:
            return Response({"error": "La date est requise."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Convertir la date en objet `date`
        try:
            date_obj = datetime.strptime(date_selectionnee, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Format de date invalide."}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer les créneaux disponibles pour cette date
        creneaux_disponibles = Creneau.objects.filter(date=date_obj, disponible=True)

        # Préparer la réponse avec les créneaux disponibles
        creneaux_data = [
            {
                "id": creneau.id,
                "heure_debut": creneau.heure_debut.strftime("%H:%M"),
                "heure_fin": creneau.heure_fin.strftime("%H:%M")
            }
            for creneau in creneaux_disponibles
        ]

        return Response({"creneaux_disponibles": creneaux_data}, status=status.HTTP_200_OK)

available_creneaux_view = AvailableCreneauxAPIView.as_view()

    



class CreateReservationAPIView(APIView):
    
    

    def post(self, request, *args, **kwargs):
        creneau_id = request.data.get('creneau_id')
        nom = request.data.get('nom')
        prenom = request.data.get('prenom')
        email = request.data.get('email')
        
        # Vérifiez si le créneau est encore disponible
        creneau = Creneau.objects.get(id=creneau_id)
        if not creneau.disponible:
            return Response({"error": "Ce créneau est déjà réservé."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer une réservation
        reservation = Reservation.objects.create(
            creneau=creneau,
            nom=nom,
            prenom=prenom,
            email=email,
        )
        
        # Marquer le créneau comme réservé
        creneau.disponible = False
        creneau.save()

        # Envoi de l'email de confirmation
        self.send_confirmation_email(reservation)

        return Response({"message": "Réservation confirmée"}, status=status.HTTP_201_CREATED)

    def send_confirmation_email(self, reservation):
        subject = "Confirmation de votre réservation"
        message = f"""
        Bonjour {Reservation.nom} {Reservation.prenom},

        Votre réservation a été confirmée pour le {Reservation.date_debut_booking} à {Reservation.heure}.
        Votre numéro de réservation est : {Reservation.numero_reservation}

        Utilisez ce numéro pour consulter votre réservation.

        Cordialement,
        L'équipe de réservation
        """
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [reservation.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            print(" Email envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")


    
create_reservation_view = CreateReservationAPIView.as_view()







class UpdateReservationApiView(generics.UpdateAPIView):
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_object(self):
        """Récupère l'objet en fonction du numéro de réservation."""
        numero_reservation = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero_reservation)

update_reservation_view = UpdateReservationApiView.as_view()


class CancelReservationApiView(generics.DestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_object(self):
        """Récupère la réservation à annuler en fonction du numéro de réservation."""
        numero_reservation = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero_reservation)

    def delete(self, request, *args, **kwargs):
        """Permet d'annuler une réservation uniquement 4h avant le début."""
        Reservation = self.get_object()
        reservation_time = datetime.combine(Reservation.date_debut_booking, Reservation.heure)

        # Vérifie si l'annulation se fait plus de 4 heures avant la réservation
        if reservation_time.tzinfo is None:
            reservation_time = make_aware(reservation_time)

        # Si now() est aware, on la compare avec reservation_time aware
        current_time = now()

        if reservation_time - current_time < timedelta(hours=4):
            return Response(
                {"error": "Vous ne pouvez annuler que jusqu'à 4 heures avant."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Envoi du mail d'annulation
        self.send_cancellation_email(Reservation)

        # Suppression de la réservation de la base de données
        Reservation.delete()

        return Response({"message": "Réservation annulée avec succès et un email de confirmation a été envoyé."}, status=status.HTTP_200_OK)

    def send_cancellation_email(self, reservation):
        """Envoie un email à l'utilisateur pour confirmer l'annulation de la réservation."""
        subject = f"Annulation de votre réservation #{Reservation.numero_reservation}"
        message = f"Bonjour {Reservation.prenom} {Reservation.nom},\n\nVotre réservation #{Reservation.numero_reservation} a été annulée avec succès.\n\nMerci pour votre compréhension."
        recipient_email = Reservation.email

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,  
            [recipient_email],
            fail_silently=False,
        )

cancel_reservation_view = CancelReservationApiView.as_view()





class RetrieveReservationApiView(generics.RetrieveAPIView):
    serializer_class = ReservationSerializer
    queryset = Reservation.objects.all()

    def get_object(self):
        """Récupère la réservation spécifique en fonction du numéro de réservation."""
        numero_reservation = self.kwargs["numero_reservation"]
        return get_object_or_404(Reservation, numero_reservation=numero_reservation)

retrieve_reservation_view = RetrieveReservationApiView.as_view()

